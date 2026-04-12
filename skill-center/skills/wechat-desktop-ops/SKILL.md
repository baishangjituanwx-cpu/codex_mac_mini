---
name: wechat-desktop-ops
description: Use this skill when the user wants to operate WeChat desktop on macOS, read or send chat content through the desktop client, troubleshoot unread detection or macOS permissions, or run and repair the local auto-reply watcher in /Users/z/Downloads/Codex/scripts.
---

# WeChat Desktop Ops

## Overview

Use this skill for Mac WeChat desktop work: foreground control, OCR-based chat scanning, sending replies, hidden-idle unread watching, and macOS permission troubleshooting. This skill assumes the live automation scripts are in:

- `/Users/z/Downloads/Codex/scripts/wechat_assistant.swift`
- `/Users/z/Downloads/Codex/scripts/wechat_autoreply.py`

Read `/Users/z/.codex/skills/wechat-desktop-ops/references/official-notes.md` for official platform notes and permission requirements. Read `/Users/z/.codex/skills/wechat-desktop-ops/references/local-automation-playbook.md` for the current workspace behavior and failure modes.

## Quick Start

1. Verify runtime:
   ```bash
   python3 /Users/z/.codex/skills/wechat-desktop-ops/scripts/check_wechat_runtime.py
   ```
2. Check watcher status:
   ```bash
   python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py status
   ```
3. Start detached watcher:
   ```bash
   python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py start
   ```
4. Stop watcher:
   ```bash
   python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py stop
   ```

## Preconditions

- WeChat must be installed, logged in, and left running. Hidden is fine; fully quitting WeChat is not.
- macOS must allow the automation chain to control the UI:
  - Accessibility
  - Automation
  - Input Monitoring
  - Screen & System Audio Recording
- If unread detection matters while hidden, keep WeChat notifications and Dock badge behavior available.
- Do not test send flows against live customers. Use `文件传输助手` unless the user explicitly wants a live reply.

## Core Commands

Use the Swift helper for direct WeChat desktop actions:

```bash
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift app-state
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift current-chat
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift scan
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift send "陈永俊 AI算力" "在，你说"
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift latest-incoming "陈永俊 AI算力"
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift latest-incoming-current
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift menu-unread
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift dock-unread
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift finalize-draft "在，你说"
```

Use the Python watcher for automatic replies:

```bash
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py once
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py start
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py watch
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py status
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py stop
```

## Operating Workflow

### 1. Read the current left-hand chat list

Run:

```bash
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift scan
```

This activates WeChat, captures a screenshot, OCRs the visible left column, and returns chat name, preview, time, and click position.

Use this when:

- the user wants to know which chats are currently visible
- you need to seed watcher state
- unread exists but you need to inspect what is visible before replying

### 2. Read the latest message in a specific chat

Run:

```bash
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift latest-incoming "聊天名"
```

Use this when the preview is empty, truncated, or polluted by OCR noise.

### 3. Send a reply

Run:

```bash
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift send "聊天名" "回复内容"
```

The current implementation verifies send success through OCR after Enter. If primary send fails but the draft remains in the input box, use:

```bash
swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift finalize-draft "回复内容"
```

### 4. Run hidden-idle auto reply

Run:

```bash
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py start
```

Current watcher policy in this workspace:

- hidden when idle
- wake on unread badge
- if WeChat is frontmost with an open chat, poll the current chat even when no unread badge appears
- private chats only
- group chats reply only after `@我` is detected, then stay in a limited continuous-chat window
- group chats and notice-style chats skipped
- replies are now built from the latest incoming text plus recent turns in local chat history
- no cloud model is used by default; current behavior is local context-aware composition, not fixed single-line keyword templates
- platform materials sent only when the other side explicitly asks for homepage, links, or accounts

## Troubleshooting

### `WeChat is not running`

- Open WeChat and confirm it is logged in.
- Re-run:
  ```bash
  python3 /Users/z/.codex/skills/wechat-desktop-ops/scripts/check_wechat_runtime.py
  ```
- The watcher can stay alive while WeChat is closed, but it cannot read or send anything until the app is running again.

### Unread exists but watcher does not wake

- Check:
  ```bash
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift app-state
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift menu-unread
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift dock-unread
  ```
- The current watcher prefers the WeChat menu bar unread count and falls back to the Dock badge.
- If both are blank, inspect notification and badge settings in macOS and WeChat.

### The other side replies in the open chat, but no unread badge appears

- Check:
  ```bash
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift app-state
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift current-chat
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift latest-incoming-current
  ```
- The current watcher now polls the frontmost chat directly when WeChat is already open and active.
- This avoids relying only on menu bar or Dock unread indicators for ongoing back-and-forth conversations.

### Draft appears in input but message is not sent

- Run:
  ```bash
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift finalize-draft "同一条草稿"
  ```
- The watcher already uses this as a fallback after primary send failure.

### Right chat pane is blank or wrong chat is active

- Bring WeChat frontmost:
  ```bash
  swift /Users/z/Downloads/Codex/scripts/wechat_assistant.swift show
  ```
- Re-scan or re-read the target chat before sending.
- Do not trust state files alone. Treat visible green outgoing bubbles or cleared draft state as the send truth source.

### OCR reads the contact name incorrectly

- The current workspace normalizes known variants such as `陈永俊` + `AI算力`.
- When adding new fragile contacts, normalize them in both Swift and Python before relying on automation.

## Safety Rules

- Do not reply in group chats unless the user explicitly changes that policy.
- In this workspace, the current exception is: group chats may reply when the message clearly `@` mentions you, and the group stays active for a short follow-up window.
- Skip acknowledgment-only messages such as `好的` or `收到`.
- Never invent homepage or account materials; source them from the workspace or the user’s provided materials.
- Avoid test sends to real contacts. Prefer `文件传输助手`.

## Reference Files

- Official notes: `/Users/z/.codex/skills/wechat-desktop-ops/references/official-notes.md`
- Local playbook: `/Users/z/.codex/skills/wechat-desktop-ops/references/local-automation-playbook.md`
- Runtime check: `/Users/z/.codex/skills/wechat-desktop-ops/scripts/check_wechat_runtime.py`
