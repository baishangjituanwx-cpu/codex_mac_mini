#!/usr/bin/env python3

from __future__ import annotations

import json
import plistlib
from pathlib import Path


def parse_version(version: str) -> tuple[int, ...]:
    parts = []
    for item in version.split("."):
        try:
            parts.append(int(item))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def version_at_least(version: str, baseline: str) -> bool:
    left = parse_version(version)
    right = parse_version(baseline)
    max_len = max(len(left), len(right))
    left += (0,) * (max_len - len(left))
    right += (0,) * (max_len - len(right))
    return left >= right


def find_wechat_info() -> Path | None:
    candidates = [
        Path("/Applications/WeChat.app/Contents/Info.plist"),
        Path.home() / "Applications/WeChat.app/Contents/Info.plist",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main() -> None:
    info_path = find_wechat_info()
    payload: dict[str, object] = {
        "app_found": False,
        "info_plist": None,
        "version": None,
        "build": None,
        "moments_posting_public_baseline": "3.1.1",
        "channels_entry_public_baseline": "3.3.0",
        "channels_to_moments_public_baseline": "3.4.0.2",
        "desktop_ui_unified_baseline": "4.0.6",
        "group_share_note": "Desktop group-share path should be live-verified in the current UI.",
    }

    if not info_path:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    with info_path.open("rb") as fh:
        info = plistlib.load(fh)

    version = info.get("CFBundleShortVersionString", "")
    build = info.get("CFBundleVersion", "")
    payload.update(
        {
            "app_found": True,
            "info_plist": str(info_path),
            "version": version,
            "build": build,
            "moments_posting_likely_supported": version_at_least(version, "3.1.1"),
            "channels_entry_likely_supported": version_at_least(version, "3.3.0"),
            "channels_to_moments_likely_supported": version_at_least(version, "3.4.0.2"),
            "desktop_ui_likely_unified_with_windows": version_at_least(version, "4.0.6"),
            "assessment": (
                "Installed version is newer than the public baselines for Moments posting, "
                "native Channels entry, and Channels-to-Moments sharing. "
                "Exact group-share buttons should still be verified in the live desktop UI."
            ),
        }
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
