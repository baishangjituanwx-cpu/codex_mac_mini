---
name: wechat-channels-launchagent-keepalive
description: Use when maintaining or troubleshooting the local WeChat Channels keepalive flow that opens a fresh Chrome tab to the WeChat Channels backend and then auto-closes that just-opened tab. On macOS the current scheduler is LaunchAgent; on Windows use the bundled PowerShell launcher plus Task Scheduler.
---

# WeChat Channels LaunchAgent Keepalive

Use this skill for the current 视频号保活 implementation and its Windows equivalent.

## Current Execution Paths

- macOS:
  - The active scheduler is macOS LaunchAgent, not Codex cron.
  - LaunchAgent file:
    `/Users/baishangjituan/Library/LaunchAgents/com.codex.wechat-channels-keepalive.plist`
  - Active script:
    `/Users/baishangjituan/.codex/automations/wechat-channels-keepalive/keepalive.sh`
  - Log directory:
    `/Users/baishangjituan/.codex/automations/wechat-channels-keepalive/logs/`
- Windows equivalent:
  - Scheduler: Windows Task Scheduler.
  - Manual launcher:
    `scripts/run-keepalive.ps1`
  - Task registration helper:
    `scripts/register-keepalive-task.ps1`
  - Browser requirement:
    Start Chrome or Edge with CDP first, for example via `C:/path/to/repo/automation/python-platform-takeover/scripts/start-chrome-cdp.ps1`.

## What The Script Does

Every 40 minutes it should:

1. Check `opencli doctor` only for logging context.
2. In the current Google Chrome GUI session, open a fresh tab to:
   `https://channels.weixin.qq.com/platform/post/list`
3. Wait briefly for the page to load.
4. Read the new tab's title and final URL.
5. Close only that newly opened tab.
6. Restore the previously active tab.

This flow intentionally does not reuse an existing 视频号助手 tab.

On Windows, the repo equivalent uses Playwright-over-CDP to create that fresh tab, inspect the final page URL and title, close only the new tab, and then bring the previously known tab back to the front.

## Operating Rules

- Do not publish content.
- Do not edit drafts.
- Do not change account settings.
- Prefer validating by running the keepalive script directly once before changing LaunchAgent timing.
- If the user asks whether Codex app automation is the active executor, the answer is no: Codex automation is retained for record/history and should stay paused unless the user explicitly wants to change architecture again.
- On Windows, prefer Task Scheduler over a persistent terminal loop.

## Common Checks

- LaunchAgent status:
  `launchctl print gui/$(id -u)/com.codex.wechat-channels-keepalive`
- Reload LaunchAgent:
  `launchctl bootout gui/$(id -u) /Users/baishangjituan/Library/LaunchAgents/com.codex.wechat-channels-keepalive.plist >/dev/null 2>&1 || true`
  `launchctl bootstrap gui/$(id -u) /Users/baishangjituan/Library/LaunchAgents/com.codex.wechat-channels-keepalive.plist`
- Manual test run:
  `/Users/baishangjituan/.codex/automations/wechat-channels-keepalive/keepalive.sh`
- Recent logs:
  `tail -n 20 /Users/baishangjituan/.codex/automations/wechat-channels-keepalive/logs/keepalive-$(date '+%Y%m%d').log`
- Windows CDP browser start:
  `powershell -ExecutionPolicy Bypass -File C:/path/to/repo/automation/python-platform-takeover/scripts/start-chrome-cdp.ps1`
- Windows manual test:
  `powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/wechat-channels-launchagent-keepalive/scripts/run-keepalive.ps1`
- Windows scheduler registration:
  `powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/wechat-channels-launchagent-keepalive/scripts/register-keepalive-task.ps1`

## Success Signal

Treat the run as successful when the script returns structured JSON including:

- `ok: true`
- `status: "opened"`
- `tabClosed: true`
- `pageUrl: "https://channels.weixin.qq.com/platform/post/list"`

## Failure Interpretation

- `chrome_not_running`: Chrome GUI session was not reachable.
- `cdp_unreachable`: Windows CDP endpoint was not reachable.
- `need_login`: New tab opened but landed on login page instead of the backend list page.
- `need_verify`: New tab opened but landed on extra verification.
- `unexpected_page`: New tab opened but did not land on the expected backend route.
- Any AppleScript connection error usually means the current GUI session was not accessible from that run context.
