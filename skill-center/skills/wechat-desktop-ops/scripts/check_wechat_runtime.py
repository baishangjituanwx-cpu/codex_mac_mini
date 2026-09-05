#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
from pathlib import Path

WORKSPACE = Path("/Users/z/Downloads/Codex")
ASSISTANT = WORKSPACE / "scripts" / "wechat_assistant.swift"
WATCHER = WORKSPACE / "scripts" / "wechat_autoreply.py"
CLICLICK = Path("/Users/z/.homebrew/brew/bin/cliclick")


def run(cmd: list[str]) -> tuple[bool, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout or result.stderr).strip()
    return result.returncode == 0, output


def main() -> None:
    ok, watcher_status = run(["python3", str(WATCHER), "status"])
    wechat_ok, _ = run(["pgrep", "-x", "WeChat"])
    menu_ok, menu_output = run(["swift", str(ASSISTANT), "menu-unread"])
    dock_ok, dock_output = run(["swift", str(ASSISTANT), "dock-unread"])

    payload = {
        "workspace": str(WORKSPACE),
        "assistant_exists": ASSISTANT.exists(),
        "watcher_exists": WATCHER.exists(),
        "cliclick_exists": CLICLICK.exists(),
        "wechat_running": wechat_ok,
        "watcher_status_ok": ok,
        "watcher_status": watcher_status,
        "menu_unread_ok": menu_ok,
        "menu_unread": menu_output,
        "dock_unread_ok": dock_ok,
        "dock_unread": dock_output,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
