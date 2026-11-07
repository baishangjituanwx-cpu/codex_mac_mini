from __future__ import annotations

from social_publisher.browser import BrowserController, BrowserSessionConfig


class FakePage:
    def __init__(self, url: str):
        self.url = url
        self.brought_to_front = False
        self.goto_calls: list[tuple[str, str]] = []

    def bring_to_front(self) -> None:
        self.brought_to_front = True

    def goto(self, url: str, *, wait_until: str) -> None:
        self.goto_calls.append((url, wait_until))
        self.url = url


class FakeContext:
    def __init__(self, pages: list[FakePage] | None = None):
        self.pages = pages or []

    def new_page(self) -> FakePage:
        page = FakePage("about:blank")
        self.pages.append(page)
        return page


class FakeBrowser:
    def __init__(self, contexts: list[FakeContext]):
        self.contexts = contexts


def test_open_or_activate_page_reuses_matching_tab() -> None:
    existing = FakePage("https://example.com/editor?id=1")
    controller = BrowserController(BrowserSessionConfig(cdp_url="http://127.0.0.1:9222"))
    controller._browser = FakeBrowser([FakeContext([existing])])  # type: ignore[assignment]

    page = controller.open_or_activate_page(
        "https://example.com/editor",
        reuse_contains="example.com/editor",
    )

    assert page is existing
    assert existing.brought_to_front is True
    assert existing.goto_calls == []


def test_open_or_activate_page_creates_page_when_missing() -> None:
    context = FakeContext()
    controller = BrowserController(BrowserSessionConfig(cdp_url="http://127.0.0.1:9222"))
    controller._browser = FakeBrowser([context])  # type: ignore[assignment]

    page = controller.open_or_activate_page("https://example.com/new")

    assert page.url == "https://example.com/new"
    assert page.goto_calls == [("https://example.com/new", "domcontentloaded")]
    assert page.brought_to_front is True
    assert context.pages == [page]


def test_open_or_activate_page_force_new_skips_existing_match() -> None:
    existing = FakePage("https://example.com/editor")
    context = FakeContext([existing])
    controller = BrowserController(BrowserSessionConfig(cdp_url="http://127.0.0.1:9222"))
    controller._browser = FakeBrowser([context])  # type: ignore[assignment]

    page = controller.open_or_activate_page(
        "https://example.com/editor",
        reuse_contains="example.com/editor",
        force_new=True,
    )

    assert page is not existing
    assert page.url == "https://example.com/editor"
    assert existing.brought_to_front is False
    assert page.goto_calls == [("https://example.com/editor", "domcontentloaded")]
    assert context.pages == [existing, page]
