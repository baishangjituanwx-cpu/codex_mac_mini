#!/usr/bin/env python3
"""Windows-friendly keepalive helper for the WeChat Channels backend."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright


DEFAULT_TARGET_URL = "https://channels.weixin.qq.com/platform/post/list"
DEFAULT_CDP_URL = "http://127.0.0.1:9222"


def classify_page(url: str, target_url: str) -> tuple[bool, str]:
    lowered = url.lower()
    if url.startswith(target_url):
        return True, "opened"
    if any(token in lowered for token in ("login", "scanlogin", "qrcode")):
        return False, "need_login"
    if any(token in lowered for token in ("verify", "captcha")):
        return False, "need_verify"
    return False, "unexpected_page"


def build_result(**extra: Any) -> dict[str, Any]:
    result = {
        "ok": False,
        "status": "unknown",
        "targetUrl": DEFAULT_TARGET_URL,
        "pageUrl": "",
        "pageTitle": "",
        "tabClosed": False,
        "restoredPreviousTab": False,
    }
    result.update(extra)
    return result


def safe_bring_to_front(page: Page | None) -> bool:
    if page is None:
        return False
    try:
        if page.is_closed():
            return False
        page.bring_to_front()
        return True
    except PlaywrightError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--wait-seconds", type=float, default=4.0)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()

    result = build_result(targetUrl=args.target_url)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(args.cdp_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            previous_pages = list(context.pages)
            previous_page = previous_pages[-1] if previous_pages else None
            page = context.new_page()
            try:
                page.goto(
                    args.target_url,
                    wait_until="domcontentloaded",
                    timeout=int(args.timeout_seconds * 1000),
                )
                if args.wait_seconds > 0:
                    page.wait_for_timeout(int(args.wait_seconds * 1000))
                result["pageUrl"] = page.url
                result["pageTitle"] = page.title()
                ok, status = classify_page(page.url, args.target_url)
                result["ok"] = ok
                result["status"] = status
            finally:
                try:
                    page.close()
                    result["tabClosed"] = True
                except PlaywrightError:
                    result["tabClosed"] = False

            result["restoredPreviousTab"] = safe_bring_to_front(previous_page)
    except PlaywrightError as exc:
        message = str(exc)
        status = "cdp_unreachable" if "connect" in message.lower() else "chrome_not_running"
        result = build_result(
            status=status,
            targetUrl=args.target_url,
            error=message,
        )
    except Exception as exc:  # pragma: no cover - defensive wrapper for operator runs
        result = build_result(
            status="unexpected_error",
            targetUrl=args.target_url,
            error=str(exc),
        )

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
