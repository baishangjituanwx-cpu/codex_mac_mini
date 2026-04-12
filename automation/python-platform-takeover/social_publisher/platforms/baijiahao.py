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
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
)


class BaijiahaoPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="baijiahao",
        display_name="百家号",
        compose_urls=["https://baijiahao.baidu.com"],
        management_urls=["https://baijiahao.baidu.com/builder/rc/content"],
        prechecks=[
            "先查作品管理 / 内容管理，确认同标题没重复",
            "接管旧标签页前先重读标题和正文",
            "封面优先用本地 prepared 横版封面",
        ],
        manual_checkpoints=[
            "百度安全验证",
            "登录态恢复",
            "封面上传后人工复核",
        ],
        success_signals=[
            "编辑页出现提交成功，正在审核中",
            "作品管理 / 内容管理出现新条目",
        ],
        takeover_allowed=[
            "标题、正文、封面都还是本次发布包的图文编辑页",
            "卡在安全验证前后的同一条半成品页",
        ],
        takeover_stop_conditions=[
            "作品管理已经有同标题记录",
            "当前页残留的是旧文章草稿",
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
        mapping = load_platform_mapping("baijiahao")
        title_marker = content_snippet(platform_content.title, limit=24)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="builder/rc/content",
        )
        if self._is_login_gate(management_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="百家号当前停在登录检查点，先人工恢复登录态再继续。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(management_page, mapping, title_marker)
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="百家号作品管理里已经有同标题记录，停止重复发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[f"matched_title: {title_marker}"],
            )

        compose_page = self._open_editor(controller, mapping)
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="百家号编辑页当前停在登录检查点，先人工恢复登录态再继续。",
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
                message="百家号当前标签页残留的是旧草稿内容，停止接管。",
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
                message="百家号接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, mapping)
        if self._is_safety_checkpoint(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_checkpoint_required",
                message="百家号当前进入百度安全验证，先人工完成后再从当前页继续。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes + mapping["checkpoints"]["manual"],
            )
        if self._has_success_signal(compose_page, mapping):
            notes.append("editor_signal: success")
        verified = self._find_existing_entry(
            management_page,
            mapping,
            title_marker,
            refresh=True,
        )
        if verified:
            return PublishResult(
                ok=True,
                status="submitted",
                message="百家号发布已提交，并在作品管理里确认到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="百家号已经点击提交，但还没在作品管理里确认到新条目。",
            current_url=compose_page.url,
            management_url=management_page.url,
            notes=notes,
        )

    def _open_editor(self, controller: BrowserController, mapping: dict) -> Page:
        for page in controller.find_pages_by_url("baijiahao.baidu.com"):
            if self._looks_like_editor(page, mapping):
                page.bring_to_front()
                return page
        return controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="baijiahao.baidu.com",
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
        raise RuntimeError("Unable to reach the Baijiahao article editor from the current page.")

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
        title_locator = self._maybe_first_locator(page, mapping["selectors"]["title_input_candidates"])
        body_locator = self._maybe_first_locator(page, mapping["selectors"]["body_editor_candidates"])
        current_title = self._read_locator_text(title_locator) if title_locator else ""
        current_body = self._read_locator_text(body_locator) if body_locator else ""
        normalized_title = normalize_text(title)
        normalized_body = normalize_text(body)
        if current_title and current_title not in normalized_title and normalized_title not in current_title:
            issues.append(f"existing_title: {current_title[:60]}")
        if current_body and current_body not in normalized_body and normalized_body not in current_body:
            issues.append(f"existing_body: {current_body[:80]}")
        return issues

    def _type_title(self, page: Page, mapping: dict, title: str) -> None:
        locator = self._first_locator(page, mapping["selectors"]["title_input_candidates"])
        self._clear_and_type(page, locator, title)

    def _type_body(self, page: Page, mapping: dict, body: str) -> None:
        locator = self._first_locator(page, mapping["selectors"]["body_editor_candidates"])
        self._clear_and_type(page, locator, body)

    def _upload_cover(self, page: Page, mapping: dict, cover_path: Path) -> None:
        if not cover_path.exists():
            raise FileNotFoundError(f"Cover file not found: {cover_path}")
        file_input = self._first_locator(page, mapping["selectors"]["cover_file_inputs"])
        file_input.set_input_files(str(cover_path))
        page.wait_for_timeout(1500)

    def _click_publish(self, page: Page, mapping: dict) -> None:
        self._click_button(page, mapping["buttons"]["publish"])
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
            page.wait_for_timeout(2200)
        text = normalize_text(page.locator("body").inner_text())
        statuses = mapping["verify"]["management_status"]
        return title_marker in text and any(status in text for status in statuses)

    def _has_success_signal(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["success"])

    def _is_safety_checkpoint(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["safety_verification"])

    def _is_login_gate(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["login_required"])

    def _pick_cover_path(self, assets: AssetPaths) -> Path | None:
        for candidate in (assets.cover_4_3, assets.cover_3_4):
            if candidate:
                return Path(candidate)
        return None

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
