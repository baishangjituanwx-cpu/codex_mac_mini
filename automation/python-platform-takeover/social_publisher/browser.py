from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from playwright.sync_api import Browser, Page, Playwright, sync_playwright


@dataclass
class BrowserSessionConfig:
    cdp_url: str | None = None


class BrowserController:
    def __init__(self, config: BrowserSessionConfig):
        self.config = config
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    def __enter__(self) -> "BrowserController":
        if not self.config.cdp_url:
            raise RuntimeError("BROWSER_CDP_URL is required for existing-tab takeover.")
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.connect_over_cdp(self.config.cdp_url)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    def pages(self) -> list[Page]:
        browser = self._require_browser()
        pages: list[Page] = []
        for context in browser.contexts:
            pages.extend(context.pages)
        return pages

    def find_pages_by_url(self, text: str) -> list[Page]:
        return [page for page in self.pages() if text in page.url]

    def describe_pages(self) -> Iterable[tuple[str, str]]:
        for page in self.pages():
            yield page.title(), page.url

    def _require_browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError("Browser is not connected.")
        return self._browser
