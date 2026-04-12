from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
except ModuleNotFoundError:  # pragma: no cover - runtime fallback for readiness-only usage
    class PlaywrightTimeoutError(Exception):
        pass

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

from social_publisher.browser import BrowserController
from social_publisher.content_package import AssetPaths, PlatformContent
from social_publisher.platform_mapping import load_platform_mapping
from social_publisher.platforms.base import (
    detect_text_mismatch,
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
    read_locator_text,
)


class ToutiaoPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="toutiao",
        display_name="今日头条 / 头条号",
        compose_urls=["https://mp.toutiao.com"],
        management_urls=["https://mp.toutiao.com/profile_v4/graphic/publish"],
        prechecks=[
            "入口走主页 -> 创作 -> 图文",
            "先看作品管理避免重复",
            "预览并发布后还要确认发布",
        ],
        manual_checkpoints=[
            "短信验证码",
            "登录态恢复",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中",
        ],
        takeover_allowed=[
            "标题、正文、封面都已就绪，只差二次确认的半成品页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同标题",
            "当前页卡在登录态且无法恢复",
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
        mapping = load_platform_mapping("toutiao")
        title_marker = content_snippet(platform_content.title, limit=24)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="profile_v4/graphic",
        )
        if self._is_login_gate(management_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="头条号当前停在登录/验证码检查点，先人工恢复登录态再继续。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(management_page, mapping, title_marker)
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="作品管理里已经有同标题新条目，停止发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[f"matched_title: {title_marker}"],
            )

        compose_page = self._open_editor(controller, mapping)
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="头条号编辑页停在登录/验证码检查点，先人工恢复登录态再继续。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        self._enter_compose_flow(compose_page, mapping)
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
                message="头条号当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mismatch,
            )
        self._type_title(compose_page, mapping, platform_content.title)
        self._type_body(compose_page, mapping, platform_content.description)

        notes = [f"matched_title: {title_marker}"]
        cover_path = self._pick_cover_path(assets)
        if cover_path is not None:
            self._upload_cover(compose_page, mapping, cover_path)
            notes.append(f"cover: {cover_path}")
        else:
            notes.append("cover: skipped (no cover_4_3 or cover_3_4 path)")

        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="头条号接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish_chain(compose_page, mapping)
        if self._has_success_signal(compose_page, mapping):
            notes.append("editor_signal: success")
            return PublishResult(
                ok=True,
                status="submitted",
                message="头条号发布已提交，编辑页出现了成功信号。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )
        verified = self._wait_for_existing_entry(management_page, mapping, title_marker)
        if verified:
            return PublishResult(
                ok=True,
                status="submitted",
                message="头条号发布已提交，并在作品管理里确认到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="头条号已经走完预览并发布，但还没在作品管理里确认到新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
        )

    def _open_editor(self, controller: BrowserController, mapping: dict) -> Page:
        for page in controller.find_pages_by_url("mp.toutiao.com"):
            if self._looks_like_editor(page, mapping):
                page.bring_to_front()
                return page
        return controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="mp.toutiao.com",
        )

    def _enter_compose_flow(self, page: Page, mapping: dict) -> None:
        if self._looks_like_editor(page, mapping):
            return
        for text in mapping["buttons"]["publish_entry"]:
            if self._looks_like_editor(page, mapping):
                return
            if not self._click_text_like(page, text):
                continue
            page.wait_for_timeout(1200)
        if self._looks_like_editor(page, mapping):
            return
        raise RuntimeError("Unable to reach the Toutiao graphic editor from the current page.")

    def _looks_like_editor(self, page: Page, mapping: dict) -> bool:
        return self._has_candidate(page, mapping["selectors"]["title_input_candidates"]) and self._has_candidate(
            page, mapping["selectors"]["body_editor_candidates"]
        )

    def _detect_draft_mismatch(
        self,
        page: Page,
        mapping: dict,
        title: str,
        body: str,
    ) -> list[str]:
        issues: list[str] = []
        title_input = self._first_locator(page, mapping["selectors"]["title_input_candidates"])
        body_editor = self._first_locator(page, mapping["selectors"]["body_editor_candidates"])
        title_mismatch = detect_text_mismatch(
            "title",
            read_locator_text(title_input),
            title,
            limit=60,
        )
        body_mismatch = detect_text_mismatch(
            "body",
            read_locator_text(body_editor),
            body,
        )
        if title_mismatch:
            issues.append(title_mismatch)
        if body_mismatch:
            issues.append(body_mismatch)
        return issues

    def _type_title(self, page: Page, mapping: dict, title: str) -> None:
        title_input = self._first_locator(page, mapping["selectors"]["title_input_candidates"])
        self._clear_and_type(page, title_input, title)

    def _type_body(self, page: Page, mapping: dict, body: str) -> None:
        editor = self._first_locator(page, mapping["selectors"]["body_editor_candidates"])
        self._clear_and_type(page, editor, body)

    def _upload_cover(self, page: Page, mapping: dict, cover_path: Path) -> None:
        if not cover_path.exists():
            raise FileNotFoundError(f"Cover file not found: {cover_path}")
        file_input = self._first_locator(page, mapping["selectors"]["cover_file_inputs"])
        file_input.set_input_files(str(cover_path))
        page.wait_for_timeout(1500)

    def _click_publish_chain(self, page: Page, mapping: dict) -> None:
        self._click_button(page, mapping["buttons"]["preview_publish"])
        page.wait_for_timeout(1200)
        self._click_button(page, mapping["buttons"]["confirm_publish"])
        page.wait_for_timeout(1800)

    def _find_existing_entry(
        self,
        page: Page,
        mapping: dict,
        title_marker: str,
        *,
        refresh: bool = False,
    ) -> bool:
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        text = normalize_text(page.locator("body").inner_text())
        statuses = mapping["verify"]["management_status"]
        return title_marker in text and any(status in text for status in statuses)

    def _wait_for_existing_entry(
        self,
        page: Page,
        mapping: dict,
        title_marker: str,
    ) -> bool:
        for _ in range(4):
            if self._find_existing_entry(page, mapping, title_marker, refresh=True):
                return True
            page.wait_for_timeout(1200)
        return False

    def _has_success_signal(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["success"])

    def _is_login_gate(self, page: Page, mapping: dict) -> bool:
        if "login" in page.url:
            return True
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

    def _first_locator(self, page: Page, selectors: list[str]) -> Locator:
        for selector in selectors:
            locator = page.locator(selector)
            if locator.count():
                return locator.first
        raise RuntimeError(f"Unable to locate any selector from: {selectors}")

    def _clear_and_type(self, page: Page, locator: Locator, text: str) -> None:
        locator.wait_for(timeout=8000)
        locator.click()
        page.keyboard.press(primary_select_all_shortcut())
        page.keyboard.press("Backspace")
        page.keyboard.type(text, delay=14)
        page.wait_for_timeout(400)

    def _pick_cover_path(self, assets: AssetPaths) -> Path | None:
        for candidate in (assets.cover_4_3, assets.cover_3_4):
            if candidate:
                return Path(candidate)
        return None
