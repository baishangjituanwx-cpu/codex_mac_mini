from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except ModuleNotFoundError:  # pragma: no cover - runtime fallback for readiness-only usage
    class PlaywrightTimeoutError(Exception):
        pass

if TYPE_CHECKING:
    from playwright.sync_api import Frame, Locator, Page

from social_publisher.browser import BrowserController
from social_publisher.content_package import AssetPaths, PlatformContent
from social_publisher.platform_mapping import load_platform_mapping
from social_publisher.platforms.base import (
    detect_text_mismatch,
    evaluate_takeover_field,
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    pick_takeover_candidate,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
    read_locator_text,
    TakeoverCandidate,
)


class WeChatChannelsPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="wechat_channels",
        display_name="微信视频号",
        compose_urls=[
            "https://channels.weixin.qq.com/login.html",
            "https://channels.weixin.qq.com/platform/post/create",
        ],
        management_urls=["https://channels.weixin.qq.com/micro/content/post/list"],
        prechecks=[
            "先确认 login.html 仍然有登录态",
            "真实表单在 iframe[name='content']",
            "先查列表页是否已有同视频",
        ],
        manual_checkpoints=[
            "登录失效",
            "上传卡住",
            "封面弹层需要人工复核",
        ],
        success_signals=[
            "create 页出现已发表",
            "列表页出现新条目且描述片段正确",
        ],
        takeover_allowed=[
            "视频已上传且短标题、描述已填的 ready 页",
            "删除错误成品后的同条修复页",
        ],
        takeover_stop_conditions=[
            "列表页已有同视频",
            "可见 UI 和 frame 真实状态不一致",
            "create 页跳回 login.html",
        ],
    )

    def inspect_takeover_candidates(
        self,
        controller: BrowserController,
        platform_content: PlatformContent,
    ) -> list[TakeoverCandidate]:
        mapping = load_platform_mapping("wechat_channels")
        return self._collect_compose_candidates(
            controller,
            mapping,
            platform_content.title,
            platform_content.description,
        )

    def publish(
        self,
        controller: BrowserController,
        platform_content: PlatformContent,
        assets: AssetPaths,
        *,
        dry_run: bool = False,
    ) -> PublishResult:
        mapping = load_platform_mapping("wechat_channels")
        title_marker = content_snippet(platform_content.title, limit=16)
        description_marker = content_snippet(platform_content.description)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="micro/content/post/list",
        )
        if self._is_login_gate(management_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="视频号当前停在登录检查点，先人工扫码恢复登录态再继续。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(
            management_page,
            mapping,
            title_marker,
            description_marker,
        )
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="视频号列表页已经有相同标题或描述片段，停止重复发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[
                    f"matched_title: {title_marker}",
                    f"matched_description: {description_marker}",
                ],
            )

        compose_page, frame, compose_notes = self._select_compose_page(
            controller,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="视频号 create 页跳回了登录态，先人工恢复登录态再继续。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        mismatch = self._detect_draft_mismatch(
            frame,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if mismatch:
            return PublishResult(
                ok=False,
                status="stopped_existing_draft_mismatch",
                message="视频号当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mismatch,
            )
        self._ensure_video_present(compose_page, frame, mapping, Path(assets.main_video))
        self._type_description(compose_page, frame, mapping, platform_content.description)
        self._type_short_title(compose_page, frame, mapping, platform_content.title)

        notes = compose_notes + [
            f"matched_title: {title_marker}",
            f"matched_description: {description_marker}",
        ]
        cover_path = self._pick_cover_path(assets)
        if cover_path is not None:
            self._upload_cover(compose_page, frame, mapping, cover_path)
            notes.append(f"cover: {cover_path}")
        else:
            notes.append("cover: skipped (no cover_3_4 or cover_4_3 path)")

        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="视频号接管链路已走到发表前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, frame, mapping)
        if self._has_success_signal(frame, mapping):
            return PublishResult(
                ok=True,
                status="published",
                message="视频号 create 页已经出现已发表信号。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        verified = self._find_existing_entry(
            management_page,
            mapping,
            title_marker,
            description_marker,
            refresh=True,
        )
        if verified:
            return PublishResult(
                ok=True,
                status="published",
                message="视频号发布已完成，并在列表页确认到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="视频号已经点击发表，但还没确认到 create 页或列表页的成功信号。",
            current_url=compose_page.url,
            management_url=management_page.url,
            notes=notes,
        )

    def _select_compose_page(
        self,
        controller: BrowserController,
        mapping: dict,
        short_title: str,
        description: str,
    ) -> tuple[Page, Frame, list[str]]:
        candidates = self._collect_compose_candidates(
            controller,
            mapping,
            short_title,
            description,
        )
        selected = pick_takeover_candidate(candidates)
        if selected is not None:
            selected.page.bring_to_front()
            frame = self._require_publish_frame(selected.page, mapping)
            return selected.page, frame, self._candidate_notes(selected)

        compose_page = controller.open_or_activate_page(
            self.metadata.compose_urls[1],
            reuse_contains="platform/post/create",
            force_new=True,
        )
        frame = self._require_publish_frame(compose_page, mapping)
        return compose_page, frame, ["takeover: opened_fresh_compose_tab"]

    def _collect_compose_candidates(
        self,
        controller: BrowserController,
        mapping: dict,
        short_title: str,
        description: str,
    ) -> list[TakeoverCandidate]:
        candidates: list[TakeoverCandidate] = []
        for page in controller.find_pages_by_url("platform/post/create"):
            candidate = TakeoverCandidate(page=page, score=1)
            if self._is_login_gate(page, mapping):
                candidate.stop_reasons.append("login_gate")
                candidates.append(candidate)
                continue

            try:
                frame = self._require_publish_frame(page, mapping, timeout=1500)
            except RuntimeError:
                candidate.stop_reasons.append("missing_publish_frame")
                candidates.append(candidate)
                continue

            frame_text = normalize_text(frame.locator("body").inner_text())
            if any(marker in frame_text for marker in mapping["signals"]["existing_video"]):
                candidate.score += 1
                candidate.notes.append("has_existing_video")

            description_locator = self._maybe_first_locator(
                frame,
                mapping["selectors"]["description_input_candidates"],
            )
            short_title_locator = self._maybe_first_locator(
                frame,
                mapping["selectors"]["short_title_candidates"],
            )
            for field_name, current, target, limit in (
                ("description", read_locator_text(description_locator), description, 80),
                ("short_title", read_locator_text(short_title_locator), short_title, 60),
            ):
                score, matched_field, stop_reason = evaluate_takeover_field(
                    field_name,
                    current,
                    target,
                    limit=limit,
                )
                candidate.score += score
                if matched_field:
                    candidate.matched_fields.append(matched_field)
                if stop_reason:
                    candidate.stop_reasons.append(stop_reason)
            candidates.append(candidate)
        return candidates

    def _candidate_notes(self, candidate: TakeoverCandidate) -> list[str]:
        notes = [
            "takeover: reused_existing_tab",
            f"takeover_score: {candidate.score}",
        ]
        if candidate.matched_fields:
            notes.append("takeover_fields: " + ", ".join(candidate.matched_fields))
        notes.extend(candidate.notes)
        return notes

    def _require_publish_frame(
        self,
        page: Page,
        mapping: dict,
        *,
        timeout: int = 8000,
    ) -> Frame:
        page.locator(mapping["selectors"]["publish_frame"]).first.wait_for(timeout=timeout)
        attempts = max(1, timeout // 300)
        for _ in range(attempts):
            frame = page.frame(name="content")
            if frame is not None:
                return frame
            page.wait_for_timeout(300)
        raise RuntimeError("Unable to resolve the WeChat Channels publish frame.")

    def _ensure_video_present(
        self,
        page: Page,
        frame: Frame,
        mapping: dict,
        video_path: Path,
    ) -> None:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        text = normalize_text(frame.locator("body").inner_text())
        pending_markers = mapping["signals"]["pending_upload"]
        if not any(marker in text for marker in pending_markers):
            return
        file_inputs = frame.locator(mapping["selectors"]["video_file_input"])
        if not file_inputs.count():
            raise RuntimeError("No video file input found on WeChat Channels create page.")
        file_inputs.first.set_input_files(str(video_path))
        self._wait_for_upload_settle(page, frame, mapping)

    def _detect_draft_mismatch(
        self,
        frame: Frame,
        mapping: dict,
        short_title: str,
        description: str,
    ) -> list[str]:
        issues: list[str] = []
        description_locator = self._first_locator(
            frame,
            mapping["selectors"]["description_input_candidates"],
        )
        short_title_locator = self._first_locator(
            frame,
            mapping["selectors"]["short_title_candidates"],
        )
        description_mismatch = detect_text_mismatch(
            "description",
            read_locator_text(description_locator),
            description,
        )
        short_title_mismatch = detect_text_mismatch(
            "short_title",
            read_locator_text(short_title_locator),
            short_title,
            limit=60,
        )
        if description_mismatch:
            issues.append(description_mismatch)
        if short_title_mismatch:
            issues.append(short_title_mismatch)
        return issues

    def _type_description(
        self,
        page: Page,
        frame: Frame,
        mapping: dict,
        description: str,
    ) -> None:
        locator = self._first_locator(frame, mapping["selectors"]["description_input_candidates"])
        self._clear_and_type(page, locator, description)

    def _type_short_title(
        self,
        page: Page,
        frame: Frame,
        mapping: dict,
        short_title: str,
    ) -> None:
        locator = self._first_locator(frame, mapping["selectors"]["short_title_candidates"])
        self._clear_and_type(page, locator, short_title)

    def _upload_cover(
        self,
        page: Page,
        frame: Frame,
        mapping: dict,
        cover_path: Path,
    ) -> None:
        if not cover_path.exists():
            raise FileNotFoundError(f"Cover file not found: {cover_path}")
        self._click_button(frame, mapping["buttons"]["cover_entry"])
        page.wait_for_timeout(800)
        file_input = self._cover_file_input(frame, mapping)
        file_input.set_input_files(str(cover_path))
        page.wait_for_timeout(1200)
        self._click_button(frame, mapping["buttons"]["cover_confirm"])
        page.wait_for_timeout(1200)

    def _cover_file_input(self, frame: Frame, mapping: dict) -> Locator:
        selectors = mapping["selectors"].get("cover_file_inputs", [])
        if isinstance(selectors, str):
            selectors = [selectors]
        for selector in selectors:
            file_inputs = frame.locator(selector)
            input_count = file_inputs.count()
            if not input_count:
                continue
            index = min(mapping["selectors"].get("cover_file_input_index", 0), input_count - 1)
            return file_inputs.nth(index)
        raise RuntimeError("No image cover file input found on WeChat Channels.")

    def _click_publish(self, page: Page, frame: Frame, mapping: dict) -> None:
        self._click_button(frame, mapping["buttons"]["publish"])
        page.wait_for_timeout(1800)

    def _find_existing_entry(
        self,
        page: Page,
        mapping: dict,
        title_marker: str,
        description_marker: str,
        *,
        refresh: bool = False,
    ) -> bool:
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2200)
        text = normalize_text(page.locator("body").inner_text())
        statuses = mapping["verify"]["management_status"]
        markers = [marker for marker in (title_marker, description_marker) if marker]
        marker_matched = any(marker in text for marker in markers)
        status_matched = any(status in text for status in statuses)
        return marker_matched and status_matched

    def _has_success_signal(self, frame: Frame, mapping: dict) -> bool:
        text = normalize_text(frame.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["success"])

    def _wait_for_upload_settle(self, page: Page, frame: Frame, mapping: dict) -> None:
        pending_markers = mapping["signals"]["pending_upload"]
        for _ in range(30):
            text = normalize_text(frame.locator("body").inner_text())
            if not any(marker in text for marker in pending_markers):
                return
            page.wait_for_timeout(1000)
        raise RuntimeError("WeChat Channels video upload did not settle in time.")

    def _is_login_gate(self, page: Page, mapping: dict) -> bool:
        if "login.html" in page.url:
            return True
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["login_required"])

    def _click_button(self, frame: Frame, names: list[str]) -> None:
        for name in names:
            button = frame.get_by_role("button", name=name)
            if not button.count():
                button = frame.get_by_text(name, exact=False)
            if not button.count():
                continue
            try:
                button.first.click(timeout=2500)
                return
            except PlaywrightTimeoutError:
                continue
        raise RuntimeError(f"Unable to locate a clickable button from: {names}")

    def _first_locator(self, frame: Frame, selectors: list[str]) -> Locator:
        locator = self._maybe_first_locator(frame, selectors)
        if locator is not None:
            return locator
        raise RuntimeError(f"Unable to locate any selector from: {selectors}")

    def _maybe_first_locator(
        self,
        frame: Frame,
        selectors: list[str],
    ) -> Locator | None:
        for selector in selectors:
            locator = frame.locator(selector)
            if locator.count():
                return locator.first
        return None

    def _clear_and_type(self, page: Page, locator: Locator, text: str) -> None:
        locator.wait_for(timeout=8000)
        locator.click()
        page.keyboard.press(primary_select_all_shortcut())
        page.keyboard.press("Backspace")
        page.keyboard.type(text, delay=14)
        page.wait_for_timeout(500)

    def _pick_cover_path(self, assets: AssetPaths) -> Path | None:
        for candidate in (assets.cover_3_4, assets.cover_4_3):
            if candidate:
                return Path(candidate)
        return None
