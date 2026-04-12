from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from social_publisher.browser import BrowserController
from social_publisher.content_package import AssetPaths, PlatformContent
from social_publisher.platform_mapping import load_platform_mapping
from social_publisher.platforms.base import (
    detect_text_mismatch,
    PlatformMetadata,
    PlatformPublisher,
    PublishResult,
    read_locator_text,
    content_snippet,
    normalize_text,
    primary_select_all_shortcut,
)


class KuaishouPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="kuaishou",
        display_name="快手",
        compose_urls=["https://cp.kuaishou.com/article/publish/video?tabType=1"],
        management_urls=["https://cp.kuaishou.com/article/manage/video"],
        prechecks=[
            "先看作品管理有无重复",
            "遇到继续编辑提示优先续作",
            "重读 #work-description-edit 的真实内容",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "上传封面后人工确认",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中",
        ],
        takeover_allowed=[
            "顶部提示继续编辑的草稿页",
            "视频已上传但还没最终提交的页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同 description 和同视频",
            "当前草稿内容和本次发布包不一致",
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
        mapping = load_platform_mapping("kuaishou")
        snippet = content_snippet(platform_content.description)
        management_page = controller.open_or_activate_page(
            self.metadata.management_urls[0],
            reuse_contains="cp.kuaishou.com/article/manage",
        )
        duplicate = self._find_existing_entry(management_page, mapping, snippet)
        if duplicate:
            return PublishResult(
                ok=False,
                status="stopped_duplicate",
                message="作品管理里已经出现相同描述片段，停止发布。",
                current_url=management_page.url,
                management_url=management_page.url,
                notes=[f"matched_snippet: {snippet}"],
            )

        compose_page = controller.open_or_activate_page(
            self.metadata.compose_urls[0],
            reuse_contains="cp.kuaishou.com/article/publish/video",
        )
        self._resume_existing_draft_if_needed(compose_page, mapping)
        mismatch = self._detect_draft_mismatch(
            compose_page,
            mapping,
            platform_content.description,
        )
        if mismatch:
            return PublishResult(
                ok=False,
                status="stopped_existing_draft_mismatch",
                message="快手当前标签页残留的是旧草稿内容，停止接管。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=[mismatch],
            )
        self._ensure_video_present(compose_page, mapping, Path(assets.main_video))
        self._type_description(compose_page, mapping, platform_content.description)

        cover_path = self._pick_cover_path(assets)
        notes: list[str] = []
        if cover_path is not None:
            self._upload_cover(compose_page, mapping, cover_path)
            notes.append(f"cover: {cover_path}")
        else:
            notes.append("cover: skipped (no cover_3_4 or cover_4_3 path)")

        if dry_run:
            return PublishResult(
                ok=True,
                status="ready",
                message="快手接管链路已走到发布前，当前是 dry-run。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes,
            )

        self._click_publish(compose_page, mapping)
        verified = self._find_existing_entry(
            management_page, mapping, snippet, refresh=True
        )
        if verified:
            return PublishResult(
                ok=True,
                status="submitted",
                message="快手发布已提交，并在作品管理里看到了新条目。",
                current_url=compose_page.url,
                management_url=management_page.url,
                notes=notes + [f"matched_snippet: {snippet}"],
            )
        return PublishResult(
            ok=False,
            status="unconfirmed",
            message="发布按钮已经点击，但还没在作品管理里确认到新条目。",
            current_url=compose_page.url,
            management_url=management_page.url,
            notes=notes + [f"matched_snippet: {snippet}"],
        )

    def _resume_existing_draft_if_needed(self, page: Page, mapping: dict) -> None:
        page.wait_for_timeout(1200)
        for text in mapping["buttons"]["continue_edit"]:
            button = page.get_by_role("button", name=text)
            if button.count():
                try:
                    button.first.click(timeout=1500)
                    page.wait_for_timeout(1200)
                    return
                except PlaywrightTimeoutError:
                    continue

    def _ensure_video_present(self, page: Page, mapping: dict, video_path: Path) -> None:
        body_text = normalize_text(page.locator("body").inner_text())
        for marker in mapping["signals"]["existing_video"]:
            if marker in body_text:
                return
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        file_inputs = page.locator(mapping["selectors"]["file_input"])
        if not file_inputs.count():
            return
        file_inputs.first.set_input_files(str(video_path))
        self._wait_for_upload_settle(page, mapping)

    def _detect_draft_mismatch(
        self,
        page: Page,
        mapping: dict,
        description: str,
    ) -> str | None:
        editor = page.locator(mapping["selectors"]["description_editor"])
        if not editor.count():
            return None
        return detect_text_mismatch(
            "description",
            read_locator_text(editor.first),
            description,
        )

    def _type_description(self, page: Page, mapping: dict, description: str) -> None:
        editor = page.locator(mapping["selectors"]["description_editor"]).first
        editor.wait_for(timeout=8000)
        editor.click()
        page.keyboard.press(primary_select_all_shortcut())
        page.keyboard.press("Backspace")
        page.keyboard.type(description, delay=18)
        page.wait_for_timeout(500)

    def _upload_cover(self, page: Page, mapping: dict, cover_path: Path) -> None:
        if not cover_path.exists():
            raise FileNotFoundError(f"Cover file not found: {cover_path}")
        for text in mapping["buttons"]["cover_entry"]:
            locator = page.get_by_text(text, exact=False)
            if locator.count():
                try:
                    locator.first.click(timeout=1500)
                    page.wait_for_timeout(800)
                    break
                except PlaywrightTimeoutError:
                    continue
        file_inputs = page.locator(mapping["selectors"]["file_input"])
        input_count = file_inputs.count()
        if not input_count:
            raise RuntimeError("No file input found for Kuaishou cover upload.")
        index = min(mapping["selectors"]["cover_file_input_index"], input_count - 1)
        file_inputs.nth(index).set_input_files(str(cover_path))
        page.wait_for_timeout(1500)

    def _click_publish(self, page: Page, mapping: dict) -> None:
        for text in mapping["buttons"]["publish"]:
            button = page.get_by_role("button", name=text)
            if button.count():
                try:
                    button.first.click(timeout=3000)
                    page.wait_for_timeout(1500)
                    return
                except PlaywrightTimeoutError:
                    continue
        raise RuntimeError("Unable to locate a clickable publish button on Kuaishou.")

    def _find_existing_entry(
        self, page: Page, mapping: dict, snippet: str, *, refresh: bool = False
    ) -> bool:
        if refresh:
            page.goto(self.metadata.management_urls[0], wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        text = normalize_text(page.locator("body").inner_text())
        statuses = mapping["verify"]["management_status"]
        return snippet in text and any(status in text for status in statuses)

    def _pick_cover_path(self, assets: AssetPaths) -> Path | None:
        for candidate in (assets.cover_3_4, assets.cover_4_3):
            if candidate:
                return Path(candidate)
        return None

    def _wait_for_upload_settle(self, page: Page, mapping: dict) -> None:
        pending_markers = mapping["signals"]["pending_upload"]
        for _ in range(20):
            text = normalize_text(page.locator("body").inner_text())
            if not any(marker in text for marker in pending_markers):
                return
            page.wait_for_timeout(1000)
