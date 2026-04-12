from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from social_publisher.browser import BrowserController
from social_publisher.content_package import AssetPaths, PlatformContent
from social_publisher.platform_mapping import load_platform_mapping
from social_publisher.platforms.base import (
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
)


class DouyinPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="douyin",
        display_name="抖音",
        compose_urls=[
            "https://creator.douyin.com/creator-micro/content/upload",
            "https://creator.douyin.com",
        ],
        management_urls=["https://creator.douyin.com/creator-micro/content/manage"],
        prechecks=[
            "先看作品管理顶部最近两条",
            "标题必须走真实输入，不能只改 input.value",
            "封面优先准备 3:4 和 4:3 两版图",
        ],
        manual_checkpoints=[
            "登录和风控验证",
            "封面裁切后人工确认",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中或已发布",
        ],
        takeover_allowed=[
            "视频已上传且标题、描述与本次发布包一致的草稿页",
            "只差最终补标题 / 补封面 / 点击发布的半成品页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同描述新条目",
            "标题或描述仍然是上一次选题",
            "当前页已经退出登录",
        ],
    )

    def publish(
        self,
        controller: BrowserController,
        platform_content: PlatformContent,
        assets: AssetPaths,
        *,
        dry_run: bool = False,
    ) -> PublishResult:
        mapping = load_platform_mapping("douyin")
        description_marker = content_snippet(platform_content.description)
        title_marker = content_snippet(platform_content.title, limit=20)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="creator-micro/content/manage",
        )
        if self._is_login_gate(management_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="抖音当前停在登录或风控检查点，先人工恢复后再继续。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(
            management_page,
            mapping,
            description_marker,
            title_marker,
        )
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="抖音作品管理里已经有相同标题或描述片段的新条目，停止重复发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[
                    f"matched_title: {title_marker}",
                    f"matched_description: {description_marker}",
                ],
            )

        compose_page = self._open_editor(controller, mapping)
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="抖音发布页当前停在登录或风控检查点，先人工恢复后再继续。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        mismatch = self._detect_draft_mismatch(
            compose_page,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if mismatch:
            return PublishResult(
                ok=False,
                status="stopped_existing_draft_mismatch",
                message="抖音当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mismatch,
            )

        self._ensure_video_present(compose_page, mapping, Path(assets.main_video))
        self._type_title(compose_page, mapping, platform_content.title)
        self._type_description(compose_page, mapping, platform_content.description)

        notes = [
            f"matched_title: {title_marker}",
            f"matched_description: {description_marker}",
        ]
        self._upload_covers(compose_page, mapping, assets, notes)

        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="抖音接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, mapping)
        if self._has_success_signal(compose_page, mapping):
            notes.append("composer_signal: success")
            return PublishResult(
                ok=True,
                status="submitted",
                message="抖音发布已提交，发布页出现了成功信号。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )
        verified = self._wait_for_existing_entry(
            management_page,
            mapping,
            description_marker,
            title_marker,
        )
        if verified:
            return PublishResult(
                ok=True,
                status="submitted",
                message="抖音发布已提交，并在作品管理里确认到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="抖音已经点击发布，但还没在作品管理里确认到新条目。",
            current_url=compose_page.url,
            management_url=management_page.url,
            notes=notes,
        )

    def _open_editor(self, controller: BrowserController, mapping: dict) -> Page:
        for page in controller.find_pages_by_url("creator.douyin.com"):
            if self._looks_like_editor(page, mapping):
                page.bring_to_front()
                return page
        return controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="creator.douyin.com",
        )

    def _looks_like_editor(self, page: Page, mapping: dict) -> bool:
        return self._has_candidate(page, mapping["selectors"]["title_input_candidates"]) and self._has_candidate(
            page, mapping["selectors"]["description_input_candidates"]
        )

    def _detect_draft_mismatch(
        self,
        page: Page,
        mapping: dict,
        title: str,
        description: str,
    ) -> list[str]:
        issues: list[str] = []
        title_locator = self._maybe_first_locator(page, mapping["selectors"]["title_input_candidates"])
        description_locator = self._maybe_first_locator(
            page, mapping["selectors"]["description_input_candidates"]
        )
        current_title = self._read_locator_text(title_locator) if title_locator else ""
        current_description = self._read_locator_text(description_locator) if description_locator else ""
        normalized_title = normalize_text(title)
        normalized_description = normalize_text(description)
        if current_title and current_title not in normalized_title and normalized_title not in current_title:
            issues.append(f"existing_title: {current_title[:60]}")
        if (
            current_description
            and current_description not in normalized_description
            and normalized_description not in current_description
        ):
            issues.append(f"existing_description: {current_description[:80]}")
        return issues

    def _ensure_video_present(self, page: Page, mapping: dict, video_path: Path) -> None:
        body_text = normalize_text(page.locator("body").inner_text())
        if any(marker in body_text for marker in mapping["signals"]["existing_video"]):
            return
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        file_input = self._first_locator(page, mapping["selectors"]["video_file_input_candidates"])
        file_input.set_input_files(str(video_path))
        self._wait_for_upload_settle(page, mapping)

    def _type_title(self, page: Page, mapping: dict, title: str) -> None:
        locator = self._first_locator(page, mapping["selectors"]["title_input_candidates"])
        self._clear_and_type(page, locator, title)

    def _type_description(self, page: Page, mapping: dict, description: str) -> None:
        locator = self._first_locator(page, mapping["selectors"]["description_input_candidates"])
        self._clear_and_type(page, locator, description)

    def _upload_covers(
        self,
        page: Page,
        mapping: dict,
        assets: AssetPaths,
        notes: list[str],
    ) -> None:
        cover_paths = [
            ("cover_3_4", assets.cover_3_4),
            ("cover_4_3", assets.cover_4_3),
        ]
        available = [(name, Path(path)) for name, path in cover_paths if path]
        if not available:
            notes.append("cover: skipped (no cover_3_4 or cover_4_3 path)")
            return
        self._click_cover_entry(page, mapping)
        file_inputs = page.locator(mapping["selectors"]["cover_file_inputs"])
        input_count = file_inputs.count()
        if not input_count:
            notes.append("cover: modal opened but no file input found")
            return
        for index, (name, path) in enumerate(available):
            if not path.exists():
                raise FileNotFoundError(f"Cover file not found: {path}")
            target_index = min(index, input_count - 1)
            file_inputs.nth(target_index).set_input_files(str(path))
            page.wait_for_timeout(1200)
            notes.append(f"{name}: {path}")
        self._click_button(page, mapping["buttons"]["cover_confirm"])
        page.wait_for_timeout(1200)

    def _click_cover_entry(self, page: Page, mapping: dict) -> None:
        self._click_button(page, mapping["buttons"]["cover_entry"])
        page.wait_for_timeout(1000)

    def _click_publish(self, page: Page, mapping: dict) -> None:
        self._click_button(page, mapping["buttons"]["publish"])
        page.wait_for_timeout(1800)

    def _find_existing_entry(
        self,
        page: Page,
        mapping: dict,
        description_marker: str,
        title_marker: str,
        *,
        refresh: bool = False,
    ) -> bool:
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2200)
        text = normalize_text(page.locator("body").inner_text())
        statuses = mapping["verify"]["management_status"]
        markers = [marker for marker in (description_marker, title_marker) if marker]
        return any(marker in text for marker in markers) and any(status in text for status in statuses)

    def _wait_for_existing_entry(
        self,
        page: Page,
        mapping: dict,
        description_marker: str,
        title_marker: str,
    ) -> bool:
        for _ in range(4):
            if self._find_existing_entry(
                page,
                mapping,
                description_marker,
                title_marker,
                refresh=True,
            ):
                return True
            page.wait_for_timeout(1200)
        return False

    def _has_success_signal(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["success"])

    def _wait_for_upload_settle(self, page: Page, mapping: dict) -> None:
        pending_markers = mapping["signals"]["pending_upload"]
        for _ in range(30):
            text = normalize_text(page.locator("body").inner_text())
            if not any(marker in text for marker in pending_markers):
                return
            page.wait_for_timeout(1000)
        raise RuntimeError("Douyin video upload did not settle in time.")

    def _is_login_gate(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["login_required"])

    def _click_button(self, page: Page, names: list[str]) -> None:
        for name in names:
            button = page.get_by_role("button", name=name)
            if not button.count():
                button = page.get_by_text(name, exact=False)
            if not button.count():
                continue
            try:
                button.first.click(timeout=2500)
                return
            except PlaywrightTimeoutError:
                continue
        raise RuntimeError(f"Unable to locate a clickable button from: {names}")

    def _has_candidate(self, page: Page, selectors: list[str]) -> bool:
        for selector in selectors:
            if page.locator(selector).count():
                return True
        return False

    def _maybe_first_locator(self, page: Page, selectors: list[str]) -> Locator | None:
        for selector in selectors:
            locator = page.locator(selector)
            if locator.count():
                return locator.first
        return None

    def _first_locator(self, page: Page, selectors: list[str]) -> Locator:
        locator = self._maybe_first_locator(page, selectors)
        if locator is None:
            raise RuntimeError(f"Unable to locate any selector from: {selectors}")
        return locator

    def _clear_and_type(self, page: Page, locator: Locator, text: str) -> None:
        locator.wait_for(timeout=8000)
        locator.click()
        page.keyboard.press(primary_select_all_shortcut())
        page.keyboard.press("Backspace")
        page.keyboard.type(text, delay=14)
        page.wait_for_timeout(500)

    def _read_locator_text(self, locator: Locator) -> str:
        try:
            value = locator.input_value(timeout=1500)
        except Exception:  # noqa: BLE001
            try:
                value = locator.inner_text(timeout=1500)
            except Exception:  # noqa: BLE001
                return ""
        return normalize_text(value)
