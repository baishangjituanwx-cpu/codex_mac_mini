# Local Automation Playbook

This file captures the current behavior of the workspace automation in `/Users/z/Downloads/Codex`.

## Active Scripts

- Swift UI helper: `/Users/z/Downloads/Codex/scripts/wechat_assistant.swift`
- Python watcher: `/Users/z/Downloads/Codex/scripts/wechat_autoreply.py`

## What the Swift Helper Does

- `scan`: activates WeChat, screenshots the desktop, OCRs the visible chat list
- `send`: switches to a target chat and sends one or more lines
- `app-state`: returns whether WeChat is running, hidden, and frontmost
- `current-chat`: OCRs the current right-pane chat header
- `latest-incoming`: OCRs the right pane to get the latest incoming message for a chat
- `latest-incoming-current`: reads the latest incoming message from the current open chat without switching chats
- `menu-unread`: reads the WeChat menu bar unread counter
- `dock-unread`: reads the Dock badge as fallback
- `finalize-draft`: presses Enter on an already present draft and verifies it cleared or became visible as a sent message

## What the Python Watcher Does

- runs in hidden-idle mode by default
- wakes only when unread is detected
- if WeChat is frontmost, also polls the currently open chat even when no unread badge exists
- reads visible chats conservatively
- replies only in private chats
- exception: group chats can reply after explicit `@我` trigger and remain active for about 15 minutes of follow-up
- skips groups, service messages, file helper, acknowledgements, and drafts
- keeps a short per-chat local history so replies can follow the recent上下文 instead of only matching the latest line
- does not call a cloud LLM by default; replies are composed locally from recent turns, detected intent, and pending asks
- sends platform materials only after explicit ask for homepage, links, or accounts

## Current Start and Stop Commands

```bash
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py start
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py status
python3 /Users/z/Downloads/Codex/scripts/wechat_autoreply.py stop
```

## Stable Runtime Assumptions

- WeChat may be hidden, but it must still be running.
- Unread detection should prefer the menu bar unread count and only fall back to the Dock badge.
- A send is trusted only when:
  - the green outgoing bubble becomes visible, or
  - the draft is cleared from the input area after Enter

## Known Failure Modes

### WeChat closed

- The watcher stays alive but cannot act.
- The old behavior spammed `WeChat is not running`; the current code suppresses repeated identical errors.

### No unread badge in the active chat

- This happens when the user is already inside the conversation window.
- The watcher should now fall back to `current-chat` + `latest-incoming-current` while WeChat is frontmost.
- This branch must not activate WeChat or switch chats, otherwise it steals focus and breaks the chat context.

### Group chat follow-up

- A group is not globally opened for auto-reply.
- The trigger is still explicit mention markers such as `［有人@我］` in the preview.
- After that trigger, the watcher keeps the group in an active session window so follow-up messages can continue without every line repeating the mention.
- When the window expires, the group returns to silent mode until the next explicit mention.

### Wrong or blank right pane

- The left chat may be highlighted while the right pane is stale or blank.
- Force WeChat frontmost and re-read before sending.

### Draft entered but not sent

- This is the main reason for apparent “already replied” false positives.
- The watcher now falls back to `finalize-draft`.

### OCR name variants

- Contact names can drift because of OCR.
- Normalize fragile names in both Swift and Python.

## Operational Lessons

- Do not treat state file updates or log lines as send truth by themselves.
- Do not run raw send tests against live customers.
- When the user reports “I saw the draft but it was not sent,” verify the right pane before assuming success.
