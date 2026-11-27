from __future__ import annotations

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
    evaluate_takeover_field,
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    pick_takeover_candidate,
    read_locator_text,
    TakeoverCandidate,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
)


class ZhihuPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="zhihu",
        display_name="知乎",
        compose_urls=["https://zhuanlan.zhihu.com/write"],
        management_urls=["https://www.zhihu.com/creator/content"],
        prechecks=[
            "先看创作中心，确认没有同标题重复内容",
            "富文本字段必须真实激活",
            "接管旧标签页前先确认标题和正文不是旧草稿",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "编辑器异常时人工重试",
        ],
        success_signals=[
            "当前页 visible 发布成功",
            "直接跳转公开文章页",
            "创作中心出现新文章",
        ],
        takeover_allowed=[
            "标题和正文都已写入，只差最终发布确认的半成品页",
            "发布按钮灰着，但文章内容仍然是本次发布包",
        ],
        takeover_stop_conditions=[
            "当前页内容和本次发布包不一致",
            "创作中心已有同标题",
            "登录态失效",
        ],
    )

    def inspect_takeover_candidates(
        self,
        controller: BrowserController,
        platform_content: PlatformContent,
    ) -> list[TakeoverCandidate]:
        mapping = load_platform_mapping("zhihu")
        return self._collect_editor_candidates(
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
        del assets
        mapping = load_platform_mapping("zhihu")
        title_marker = content_snippet(platform_content.title, limit=24)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="zhihu.com/creator/content",
        )
        if self._is_login_gate(management_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="知乎当前停在登录检查点，先人工恢复登录态再继续。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=mapping["checkpoints"]["manual"],
            )

        duplicate = self._find_existing_entry(management_page, mapping, title_marker)
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="知乎创作中心里已经有同标题新条目，停止重复发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[f"matched_title: {title_marker}"],
            )

        compose_page, compose_notes = self._select_editor_page(
            controller,
            mapping,
            platform_content.title,
            platform_content.description,
        )
        if self._is_login_gate(compose_page, mapping):
            return PublishResult(
                ok=False,
                status="manual_login_required",
                message="知乎编辑页当前停在登录检查点，先人工恢复登录态再继续。",
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
                message="知乎当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=mismatch,
            )

        self._type_title(compose_page, mapping, platform_content.title)
        self._type_body(compose_page, mapping, platform_content.description)
        self._ensure_editor_activation(compose_page, mapping)

        notes = compose_notes + [f"matched_title: {title_marker}"]
        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="知乎接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, mapping)
        if self._has_public_url(compose_page):
            notes.append(f"public_url: {compose_page.url}")
            return PublishResult(
                ok=True,
                status="published",
                message="知乎发布完成，并已进入公开文章页。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
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
                status="published",
                message="知乎发布已完成，并在创作中心确认到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="知乎已经点击发布，但还没确认到公开页或创作中心成功信号。",
            current_url=compose_page.url,
            management_url=management_page.url,
            notes=notes,
        )

    def _select_editor_page(
        self,
        controller: BrowserController,
        mapping: dict,
        title: str,
        body: str,
    ) -> tuple[Page, list[str]]:
        candidates = self._collect_editor_candidates(controller, mapping, title, body)
        selected = pick_takeover_candidate(candidates)
        if selected is not None:
            selected.page.bring_to_front()
            return selected.page, self._candidate_notes(selected)
        page = controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="zhuanlan.zhihu.com/write",
            force_new=True,
        )
        return page, ["takeover: opened_fresh_compose_tab"]

    def _collect_editor_candidates(
        self,
        controller: BrowserController,
        mapping: dict,
        title: str,
        body: str,
    ) -> list[TakeoverCandidate]:
        candidates: list[TakeoverCandidate] = []
        for page in controller.find_pages_by_url("zhuanlan.zhihu.com"):
            candidate = TakeoverCandidate(page=page, score=1)
            if self._is_login_gate(page, mapping):
                candidate.stop_reasons.append("login_gate")
                candidates.append(candidate)
                continue
            if not self._looks_like_editor(page, mapping):
                candidate.stop_reasons.append("not_editor")
                candidates.append(candidate)
                continue
            title_locator = self._maybe_first_locator(page, mapping["selectors"]["title_input_candidates"])
            body_locator = self._maybe_first_locator(page, mapping["selectors"]["body_editor_candidates"])
            for field_name, current, target, limit in (
                ("title", read_locator_text(title_locator), title, 60),
                ("body", read_locator_text(body_locator), body, 80),
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
        return notes

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

    def _ensure_editor_activation(self, page: Page, mapping: dict) -> None:
        publish_button = self._find_button(page, mapping["buttons"]["publish"])
        if publish_button is not None and self._is_button_enabled(publish_button):
            return
        editor = self._first_locator(page, mapping["selectors"]["body_editor_candidates"])
        editor.click()
        page.keyboard.type("好", delay=14)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(500)

    def _click_publish(self, page: Page, mapping: dict) -> None:
        button = self._find_button(page, mapping["buttons"]["publish"])
        if button is None:
            raise RuntimeError("Unable to locate a clickable publish button on Zhihu.")
        button.click(timeout=3000)
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

    def _has_public_url(self, page: Page) -> bool:
        return "zhuanlan.zhihu.com/p/" in page.url

    def _is_login_gate(self, page: Page, mapping: dict) -> bool:
        text = normalize_text(page.locator("body").inner_text())
        return any(marker in text for marker in mapping["signals"]["login_required"])

    def _maybe_first_locator(self, page: Page, selectors: list[str]) -> Locator | None:
        for selector in selectors:
            locator = page.locator(selector)
            if locator.count():
                return locator.first
        return None

    def _find_button(self, page: Page, names: list[str]) -> Locator | None:
        for name in names:
            button = page.get_by_role("button", name=name)
            if not button.count():
                button = page.get_by_text(name, exact=False)
            if button.count():
                return button.first
        return None

    def _is_button_enabled(self, locator: Locator) -> bool:
        try:
            return locator.is_enabled()
        except Exception:  # noqa: BLE001
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
        page.wait_for_timeout(400)

    def _read_locator_text(self, locator: Locator) -> str:
        try:
            value = locator.input_value(timeout=1500)
        except Exception:  # noqa: BLE001
            try:
                value = locator.inner_text(timeout=1500)
            except Exception:  # noqa: BLE001
                return ""
        return normalize_text(value)
