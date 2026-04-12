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


class WeiboPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="weibo",
        display_name="微博",
        compose_urls=["https://weibo.com"],
        management_urls=["https://weibo.com"],
        prechecks=[
            "先看主页流，确认没有同条重复发布",
            "接管旧标签页前先重读正文，确认不是旧草稿",
            "视频发帖优先保证正文第一屏和视频前几秒一致",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "视频上传卡住时人工复核",
        ],
        success_signals=[
            "当前页出现发布成功",
            "主页流刷新后出现新条目",
        ],
        takeover_allowed=[
            "视频已上传且正文与本次发布包一致的半成品页",
            "主页发布器里只差最终点击发布的 ready 页",
        ],
        takeover_stop_conditions=[
            "主页流已经有同正文片段的新条目",
            "当前编辑器残留的是旧主题内容",
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
        mapping = load_platform_mapping("weibo")
        description_marker = content_snippet(platform_content.description)
        home_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="weibo.com",
        )
        if self._is_login_gate(home_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="微博当前停在登录检查点，先人工恢复登录态再继续。",
                current_url=home_page.url,
                management_url=home_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(home_page, description_marker)
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="微博主页流里已经有相同正文片段，停止重复发布。",
                current_url=home_page.url,
                management_url=home_page.url,
                notes=[f"matched_description: {description_marker}"],
            )

        compose_page = self._open_editor(controller, mapping)
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="微博编辑页当前停在登录检查点，先人工恢复登录态再继续。",
                current_url=compose_page.url,
                management_url=home_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        self._enter_compose_flow(compose_page, mapping)
        mismatch = self._detect_draft_mismatch(
            compose_page,
            mapping,
            platform_content.description,
        )
        if mismatch:
            return PublishResult(
                ok=False,
                status="stopped_existing_draft_mismatch",
                message="微博当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=home_page.url,
                notes=[mismatch],
            )

        self._ensure_video_present(compose_page, mapping, Path(assets.main_video))
        self._type_description(compose_page, mapping, platform_content.description)

        notes = [f"matched_description: {description_marker}"]
        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="微博接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=home_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, mapping)
        if self._has_success_signal(compose_page, mapping):
            notes.append("composer_signal: success")
        verified = self._find_existing_entry(
            home_page,
            description_marker,
            refresh=True,
        )
        if verified:
            return PublishResult(
                ok=True,
                status="published",
                message="微博发布已完成，并在主页流里确认到了新条目。",
                current_url=compose_page.url,
                management_url=home_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="微博已经点击发布，但还没在主页流里确认到新条目。",
            current_url=compose_page.url,
            management_url=home_page.url,
            notes=notes,
        )

    def _open_editor(self, controller: BrowserController, mapping: dict) -> Page:
        for page in controller.find_pages_by_url("weibo.com"):
            if self._looks_like_editor(page, mapping):
                page.bring_to_front()
                return page
        return controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="weibo.com",
        )

    def _enter_compose_flow(self, page: Page, mapping: dict) -> None:
        if self._looks_like_editor(page, mapping):
            return
        for text in mapping["buttons"]["publish_entry"]:
            if self._looks_like_editor(page, mapping):
                return
            if not self._click_text_like(page, text):
                continue
            page.wait_for_timeout(1000)
        if self._looks_like_editor(page, mapping):
            return
        raise RuntimeError("Unable to reach the Weibo composer from the current page.")

    def _looks_like_editor(self, page: Page, mapping: dict) -> bool:
        return self._has_candidate(page, mapping["selectors"]["description_input_candidates"])

    def _detect_draft_mismatch(
        self,
        page: Page,
        mapping: dict,
        description: str,
    ) -> str | None:
        locator = self._maybe_first_locator(page, mapping["selectors"]["description_input_candidates"])
        if locator is None:
            return None
        current = self._read_locator_text(locator)
        if not current:
            return None
        target = normalize_text(description)
        if current in target or target in current:
            return None
        return f"existing_description: {current[:60]}"

    def _ensure_video_present(self, page: Page, mapping: dict, video_path: Path) -> None:
        body_text = normalize_text(page.locator("body").inner_text())
        if any(marker in body_text for marker in mapping["signals"]["existing_video"]):
            return
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        file_input = self._first_locator(page, mapping["selectors"]["video_file_input_candidates"])
        file_input.set_input_files(str(video_path))
        self._wait_for_upload_settle(page, mapping)

    def _type_description(self, page: Page, mapping: dict, description: str) -> None:
        locator = self._first_locator(page, mapping["selectors"]["description_input_candidates"])
        self._clear_and_type(page, locator, description)

    def _click_publish(self, page: Page, mapping: dict) -> None:
        self._click_button(page, mapping["buttons"]["publish"])
        page.wait_for_timeout(1800)

    def _find_existing_entry(
        self,
        page: Page,
        description_marker: str,
        *,
        refresh: bool = False,
    ) -> bool:
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        text = normalize_text(page.locator("body").inner_text())
        return description_marker in text

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
        raise RuntimeError("Weibo video upload did not settle in time.")

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

    def _click_text_like(self, page: Page, text: str) -> bool:
        candidates = (
            page.get_by_role("button", name=text),
            page.get_by_text(text, exact=False),
        )
        for locator in candidates:
            if not locator.count():
                continue
            try:
                locator.first.click(timeout=2000)
                return True
            except PlaywrightTimeoutError:
                continue
        return False

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
