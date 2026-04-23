from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Any, TYPE_CHECKING

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
        management_urls=["https://channels.weixin.qq.com/platform/post/list"],
        prechecks=[
            "先确认 login.html 仍然有登录态",
            "真实表单在 iframe[name='content']",
            "先查列表页是否已有同视频",
        ],
        manual_checkpoints=[
            "登录失效",
            "上传卡住",
            "封面状态无法自动确认",
        ],
        success_signals=[
            "create 页点击发表后，管理页新条目描述片段正确",
            "短标题、描述、封面状态都通过二次复核",
        ],
        takeover_allowed=[
            "视频已上传且短标题、描述已填的 ready 页",
            "删除错误成品后的同条修复页",
        ],
        takeover_stop_conditions=[
            "列表页已有同视频",
            "可见 UI 和 frame 真实状态不一致",
            "create 页跳回 login.html",
            "已有视频但没有匹配的标题和描述，禁止复用旧草稿",
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
        cover_path = self._pick_cover_path(assets)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="platform/post/list",
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
        management_frame = self._require_management_frame(management_page, mapping)
        management_baseline = self._capture_management_baseline(management_frame, mapping)

        duplicate = self._find_existing_entry(
            management_page,
            management_frame,
            mapping,
            required_markers=[description_marker],
            optional_markers=[title_marker],
            expected_title=platform_content.title,
            expected_description=platform_content.description,
            ignore_self_visible=True,
        )
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="视频号列表页已经有相同标题或描述片段，停止重复发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=duplicate.notes,
            )

        recent_duplicate = self._find_recent_duplicate_entry(
            management_frame,
            mapping,
            expected_title=platform_content.title,
            expected_description=platform_content.description,
            ignore_self_visible=True,
        )
        if recent_duplicate:
            return PublishResult(
                ok=False,
                status="stopped_recent_content_duplicate",
                message="视频号最近内容与当前内容包高度重复，停止发布。必须先更换标题或正文骨架。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=recent_duplicate.notes,
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
        field_issues = self._verify_compose_fields(
            frame,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if field_issues:
            return PublishResult(
                ok=False,
                status="compose_verification_failed",
                message="视频号发布前二次复核失败，短标题或描述没有稳定写入。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=field_issues,
            )

        notes = compose_notes + [
            f"matched_title: {title_marker}",
            f"matched_description: {description_marker}",
        ]
        if cover_path is not None:
            self._upload_cover(compose_page, frame, mapping, cover_path)
            notes.append(f"cover: {cover_path}")
        else:
            notes.append("cover: skipped (no cover_3_4 or cover_4_3 path)")
        post_cover_field_issues = self._verify_compose_fields(
            frame,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if post_cover_field_issues:
            return PublishResult(
                ok=False,
                status="post_cover_compose_verification_failed",
                message="视频号封面处理后，短标题或描述发生了偏移，停止发布。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes + post_cover_field_issues,
            )

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
            notes.append("create_signal: 已发表")

        verified = self._find_existing_entry(
            management_page,
            management_frame,
            mapping,
            required_markers=[description_marker],
            optional_markers=[title_marker],
            expected_title=platform_content.title,
            expected_description=platform_content.description,
            refresh=True,
            require_newer_than=management_baseline,
        )
        if verified:
            return PublishResult(
                ok=True,
                status="published",
                message="视频号发布已完成，并通过了管理页二次复核。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes + verified.notes,
            )

        return PublishResult(
            ok=False,
            status="post_publish_verification_failed",
            message="视频号已经点击发表，但管理页二次复核没有通过，不能算发布成功。",
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
            if should_stop_existing_video_candidate(
                has_existing_video="has_existing_video" in candidate.notes,
                matched_fields=candidate.matched_fields,
            ):
                candidate.stop_reasons.append("existing_video_without_matching_fields")
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

    def _require_management_frame(
        self,
        page: Page,
        mapping: dict,
        *,
        timeout: int = 8000,
    ) -> Frame:
        selector = mapping["selectors"].get(
            "management_frame",
            mapping["selectors"]["publish_frame"],
        )
        page.locator(selector).first.wait_for(timeout=timeout)
        attempts = max(1, timeout // 300)
        for _ in range(attempts):
            frame = page.frame(name="content")
            if frame is not None:
                try:
                    frame.locator("body").wait_for(timeout=500)
                except PlaywrightTimeoutError:
                    page.wait_for_timeout(300)
                    continue
                return frame
            page.wait_for_timeout(300)
        raise RuntimeError("Unable to resolve the WeChat Channels management frame.")

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
        file_inputs = frame.locator(mapping["selectors"]["cover_file_inputs"])
        input_count = file_inputs.count()
        if not input_count:
            raise RuntimeError("No cover file input found on WeChat Channels.")
        index = min(mapping["selectors"]["cover_file_input_index"], input_count - 1)
        file_inputs.nth(index).set_input_files(str(cover_path))
        page.wait_for_timeout(1200)
        self._click_button(frame, mapping["buttons"]["cover_confirm"])
        self._wait_for_cover_apply(frame, mapping, page)

    def _click_publish(self, page: Page, frame: Frame, mapping: dict) -> None:
        self._click_button(frame, mapping["buttons"]["publish"])
        page.wait_for_timeout(1800)

    def _find_existing_entry(
        self,
        page: Page,
        frame: Frame,
        mapping: dict,
        *,
        required_markers: list[str],
        optional_markers: list[str] | None = None,
        expected_title: str | None = None,
        expected_description: str | None = None,
        ignore_self_visible: bool = False,
        refresh: bool = False,
        require_newer_than: "ManagementListBaseline | None" = None,
    ) -> "ManagementEntryMatch | None":
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2200)
            frame = self._require_management_frame(page, mapping)
        statuses = mapping["verify"]["management_status"]
        optional_markers = [marker for marker in (optional_markers or []) if marker]
        selector, locator, count = self._resolve_management_entries(frame, mapping)
        if not locator or count <= 0:
            return None
        for index in range(count):
            entry = locator.nth(index)
            try:
                text = normalize_text(entry.inner_text(timeout=600))
            except Exception:  # noqa: BLE001
                continue
            if not text:
                continue
            component = self._read_management_component(entry)
            if ignore_self_visible and management_entry_is_self_visible(text, component):
                continue

            matched_markers: list[str] = []
            if expected_title is not None or expected_description is not None:
                if component is None:
                    continue
                if expected_title is not None and not text_matches_exactly(
                    component.short_title,
                    expected_title,
                ):
                    continue
                if expected_description is not None and not text_matches_exactly(
                    component.description,
                    expected_description,
                ):
                    continue
                if require_newer_than is not None and not management_entry_is_newer(
                    component,
                    baseline=require_newer_than,
                    index=index,
                    current_count=count,
                ):
                    continue
            else:
                matched = match_management_entry_text(
                    text,
                    statuses=statuses,
                    required_markers=required_markers,
                    optional_markers=optional_markers,
                )
                if matched is None:
                    continue
                matched_markers = matched.matched_markers
                if require_newer_than is not None and not management_entry_is_newer(
                    component,
                    baseline=require_newer_than,
                    index=index,
                    current_count=count,
                ):
                    continue

            status = resolve_management_status(text, statuses)
            notes = [
                f"management_selector: {selector}",
                f"management_entry_index: {index}",
                f"management_status: {status or '<missing>'}",
                f"management_count: {count}",
            ]
            if matched_markers:
                notes.extend(f"management_marker: {marker}" for marker in matched_markers)
            notes.append(f"management_excerpt: {text[:120]}")
            if component is not None:
                notes.extend(
                    [
                        f"management_object_id: {component.object_id or '<missing>'}",
                        f"management_visible_type: {component.visible_type}",
                        f"management_component_short_title: {component.short_title or '<empty>'}",
                        f"management_component_description: {component.description[:120] or '<empty>'}",
                    ]
                )
            return ManagementEntryMatch(
                selector=selector,
                index=index,
                text=text,
                status=status or "<missing>",
                matched_markers=matched_markers,
                notes=notes,
        )
        return None

    def _find_recent_duplicate_entry(
        self,
        frame: Frame,
        mapping: dict,
        *,
        expected_title: str,
        expected_description: str,
        ignore_self_visible: bool = False,
    ) -> "ManagementEntryMatch | None":
        statuses = mapping["verify"]["management_status"]
        selector, locator, count = self._resolve_management_entries(frame, mapping)
        if not locator or count <= 0:
            return None
        recent_limit = min(count, RECENT_DUPLICATE_WINDOW)
        for index in range(recent_limit):
            entry = locator.nth(index)
            try:
                text = normalize_text(entry.inner_text(timeout=600))
            except Exception:  # noqa: BLE001
                continue
            if not text:
                continue
            component = self._read_management_component(entry)
            if component is None:
                continue
            if ignore_self_visible and management_entry_is_self_visible(text, component):
                continue
            similarity = description_similarity_ratio(
                component.description,
                expected_description,
            )
            if not is_recent_duplicate_content(
                component,
                expected_title,
                expected_description,
            ):
                continue
            status = resolve_management_status(text, statuses)
            return ManagementEntryMatch(
                selector=selector,
                index=index,
                text=text,
                status=status or "<missing>",
                matched_markers=[component.short_title, f"similarity={similarity:.3f}"],
                notes=[
                    f"management_selector: {selector}",
                    f"management_entry_index: {index}",
                    f"management_status: {status or '<missing>'}",
                    f"management_recent_duplicate_title: {component.short_title or '<empty>'}",
                    f"management_recent_duplicate_similarity: {similarity:.3f}",
                    f"management_recent_duplicate_description: {component.description[:120] or '<empty>'}",
                ],
            )
        return None

    def _capture_management_baseline(
        self,
        frame: Frame,
        mapping: dict,
    ) -> "ManagementListBaseline":
        selector, locator, count = self._resolve_management_entries(frame, mapping)
        if not locator or count <= 0:
            return ManagementListBaseline(selector=selector, count=0)
        top_component = self._read_management_component(locator.nth(0))
        return ManagementListBaseline(
            selector=selector,
            count=count,
            top_object_id=top_component.object_id if top_component else "",
            top_create_time=top_component.create_time if top_component else None,
        )

    def _resolve_management_entries(
        self,
        frame: Frame,
        mapping: dict,
    ) -> tuple[str, Locator | None, int]:
        selectors = mapping["selectors"].get("management_entry_candidates", [])
        max_candidates = mapping["verify"].get("max_management_candidates", 80)
        for selector in selectors:
            locator = frame.locator(selector)
            count = min(locator.count(), max_candidates)
            if count:
                return selector, locator, count
        return "", None, 0

    def _read_management_component(
        self,
        entry: Locator,
    ) -> "ManagementEntryComponent | None":
        try:
            payload = entry.evaluate(
                """node => {
                    const vm = node && node.__vue__;
                    const post = vm && vm.$props ? vm.$props.post : null;
                    if (!post || typeof post !== "object") {
                        return null;
                    }
                    const desc = post.desc && typeof post.desc === "object" ? post.desc : {};
                    const shortTitleList = Array.isArray(desc.shortTitle) ? desc.shortTitle : [];
                    let shortTitle = "";
                    for (const item of shortTitleList) {
                        if (typeof item === "string" && item.trim()) {
                            shortTitle = item;
                            break;
                        }
                        if (item && typeof item.shortTitle === "string" && item.shortTitle.trim()) {
                            shortTitle = item.shortTitle;
                            break;
                        }
                    }
                    return {
                        object_id: typeof post.objectId === "string" ? post.objectId : "",
                        create_time: typeof post.createTime === "number" ? post.createTime : null,
                        visible_type: typeof post.visibleType === "number" ? post.visibleType : null,
                        short_title: shortTitle,
                        description: typeof desc.description === "string" ? desc.description : "",
                    };
                }"""
            )
        except Exception:  # noqa: BLE001
            return None
        return management_entry_component_from_mapping(payload)

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

    def _verify_compose_fields(
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
        current_description = normalize_text(read_locator_text(description_locator))
        current_short_title = normalize_text(read_locator_text(short_title_locator))
        if not text_matches_exactly(current_description, description):
            issues.append(f"verify_description: {current_description[:80] or '<empty>'}")
        if not text_matches_exactly(current_short_title, short_title):
            issues.append(f"verify_short_title: {current_short_title[:60] or '<empty>'}")
        return issues

    def _wait_for_cover_apply(self, frame: Frame, mapping: dict, page: Page) -> None:
        applied_markers = mapping["signals"].get("cover_applied", [])
        pending_markers = mapping["signals"].get("cover_pending", [])
        for _ in range(20):
            text = normalize_text(frame.locator("body").inner_text())
            if any(marker in text for marker in applied_markers):
                return
            page.wait_for_timeout(500)
        visible_text = normalize_text(frame.locator("body").inner_text())
        pending = [marker for marker in pending_markers if marker in visible_text]
        pending_note = f" Pending markers: {' | '.join(pending)}." if pending else ""
        raise RuntimeError(
            "WeChat Channels cover upload did not reach a confirmed applied state."
            + pending_note
        )


@dataclass(frozen=True)
class ManagementEntryTextMatch:
    status: str
    matched_markers: list[str]


@dataclass(frozen=True)
class ManagementEntryMatch:
    selector: str
    index: int
    text: str
    status: str
    matched_markers: list[str]
    notes: list[str]


@dataclass(frozen=True)
class ManagementEntryComponent:
    object_id: str = ""
    create_time: int | None = None
    visible_type: int | None = None
    short_title: str = ""
    description: str = ""


@dataclass(frozen=True)
class ManagementListBaseline:
    selector: str = ""
    count: int = 0
    top_object_id: str = ""
    top_create_time: int | None = None


RECENT_DUPLICATE_WINDOW = 5
RECENT_DUPLICATE_DESCRIPTION_SIMILARITY = 0.88


def text_matches_exactly(current: str, target: str) -> bool:
    normalized_current = normalize_text(current)
    normalized_target = normalize_text(target)
    return bool(normalized_current) and normalized_current == normalized_target


def normalize_similarity_text(value: str) -> str:
    normalized = normalize_text(value)
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", normalized)


def description_similarity_ratio(current: str, target: str) -> float:
    normalized_current = normalize_similarity_text(current)
    normalized_target = normalize_similarity_text(target)
    if not normalized_current or not normalized_target:
        return 0.0
    return SequenceMatcher(None, normalized_current, normalized_target).ratio()


def is_recent_duplicate_content(
    component: ManagementEntryComponent | None,
    expected_title: str,
    expected_description: str,
    *,
    min_description_similarity: float = RECENT_DUPLICATE_DESCRIPTION_SIMILARITY,
) -> bool:
    if component is None:
        return False
    if not text_matches_exactly(component.short_title, expected_title):
        return False
    return description_similarity_ratio(
        component.description,
        expected_description,
    ) >= min_description_similarity


def should_stop_existing_video_candidate(
    *,
    has_existing_video: bool,
    matched_fields: list[str],
) -> bool:
    if not has_existing_video:
        return False
    return bool({"description", "short_title"}.difference(matched_fields))


def match_management_entry_text(
    text: str,
    *,
    statuses: list[str],
    required_markers: list[str],
    optional_markers: list[str],
) -> ManagementEntryTextMatch | None:
    normalized_text = normalize_text(text)
    if not normalized_text:
        return None
    matched_status = next((status for status in statuses if status in normalized_text), None)
    if matched_status is None:
        return None
    required = [marker for marker in required_markers if marker]
    if any(marker not in normalized_text for marker in required):
        return None
    matched_markers = required + [marker for marker in optional_markers if marker in normalized_text]
    return ManagementEntryTextMatch(
        status=matched_status,
        matched_markers=matched_markers,
    )


def resolve_management_status(text: str, statuses: list[str]) -> str | None:
    normalized_text = normalize_text(text)
    if not normalized_text:
        return None
    return next((status for status in statuses if status in normalized_text), None)


def management_entry_component_from_mapping(
    payload: dict[str, Any] | None,
) -> ManagementEntryComponent | None:
    if not isinstance(payload, dict):
        return None
    object_id = payload.get("object_id")
    create_time = payload.get("create_time")
    visible_type = payload.get("visible_type")
    short_title = payload.get("short_title")
    description = payload.get("description")
    return ManagementEntryComponent(
        object_id=object_id if isinstance(object_id, str) else "",
        create_time=create_time if isinstance(create_time, int) else None,
        visible_type=visible_type if isinstance(visible_type, int) else None,
        short_title=normalize_text(short_title if isinstance(short_title, str) else ""),
        description=normalize_text(description if isinstance(description, str) else ""),
    )


def management_entry_is_self_visible(
    text: str,
    component: ManagementEntryComponent | None,
) -> bool:
    if component is not None and component.visible_type == 3:
        return True
    return "仅自己可见" in normalize_text(text)


def management_entry_is_newer(
    component: ManagementEntryComponent | None,
    *,
    baseline: ManagementListBaseline,
    index: int,
    current_count: int,
) -> bool:
    if baseline.count <= 0:
        return True
    if current_count > baseline.count:
        return True
    if index != 0:
        return False
    if component is None:
        return False
    if baseline.top_object_id and component.object_id and component.object_id != baseline.top_object_id:
        return True
    if (
        baseline.top_create_time is not None
        and component.create_time is not None
        and component.create_time > baseline.top_create_time
    ):
        return True
    return False
