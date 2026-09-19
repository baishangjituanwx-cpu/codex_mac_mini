---
name: hermes-feishu-operator
description: Safely monitor Hermes Feishu replies, decide when Codex should intervene, generate the next Hermes prompt, and optionally paste/send it through the foreground Feishu or Lark chat only after verifying the chat is the Hermes bot `hermes_agent_mac_mini`.
---

# Hermes Feishu Operator

Use this skill when Codex is monitoring Hermes through Feishu/Lark and the user wants Codex to take over the operational loop: inspect the latest Hermes status, generate the next prompt, and, when appropriate, send it to Hermes from the foreground desktop chat.

## Hard Goal

Keep Hermes moving toward the same multi-platform content publishing capability as the Codex `push` project while keeping both executors independent. Codex and Hermes must use stable handoff/status files, not each other's chat history, and both must obey duplicate-use guards before any real publishing.

## Send Gate

Never send a Feishu/Lark message unless all checks pass:

1. Latest local Hermes state shows intervention is useful: a stuck session, incorrect conclusion, failed test that needs a narrow next prompt, or explicit user request to send.
2. The prompt is current and specific to the latest local state, not a stale prompt from an older turn.
3. The foreground app is Feishu/Lark.
4. The visible chat is the Hermes bot chat and contains `hermes_agent_mac_mini`.
5. The prompt repeats the active safety boundaries:
   - Do not test Xiaohongshu.
   - Do not use `--allow-live`.
   - Do not real publish, upload, or submit.
   - Do not modify `/Users/baishangjituan/Documents/push`.
   - Do not modify `SKILL.md`, references, or memory unless the user explicitly authorized it.
   - Restrict writable files to the latest authorized file list.

If any check fails, do not paste or send. Report the blocker and provide the prompt for manual sending.

## Workflow

1. Inspect current Hermes state from local files first:
   - `/Users/baishangjituan/.hermes/logs/gateway.log`
   - `/Users/baishangjituan/.hermes/sessions/sessions.json`
   - latest `/Users/baishangjituan/.hermes/sessions/session_*.json`
   - relevant test output under `/tmp/hermes-platform-test/**` or the active Hermes test output directory
   - stable handoff/receipt/lock files under the `python-platform-takeover` project
2. Decide whether to intervene. Prefer waiting when Hermes has produced new output in the last five minutes and is actively running a bounded command.
3. Draft one concise Hermes prompt. Include the current diagnosis, exact allowed files, exact verification commands, and the safety boundaries.
4. Prefer GUI operation when the user wants chat-flow inspection.
5. Validate the foreground Feishu/Lark app with the launcher. If desktop automation cannot expose the expected chat text, take a fresh screenshot and use image inspection to visually confirm the header/input placeholder contains `hermes_agent_mac_mini`.
6. If the user explicitly asked Codex to send, or the monitoring logic clearly requires intervention, paste/send through the verified chat only after re-checking the local safety boundaries.
7. After sending, re-check the latest Hermes session within a few minutes before issuing another prompt. Avoid stacked prompts unless Hermes is clearly idle or wrong.

## Bot Identity

The Hermes Feishu bot identity for this machine is:

```text
hermes_agent_mac_mini
```

Recognize the right conversation from the Feishu/Lark chat header or input placeholder. Similar bot names, other automation bots, group chats, or sidebars are not acceptable.

## Script Modes

Both launchers support these modes:

- `validate-only`: verify foreground app and visible chat only; no clipboard, paste, or send
- `paste-only`: verify chat, paste the message into the input box, but do not send
- `clear-only`: verify chat, clear the current input box, but do not paste/send
- `send`: verify chat, paste the message, then click the send button
- `visual-confirmed`: allow paste/send after Codex has just visually confirmed a screenshot shows `hermes_agent_mac_mini`; use only when UI text inspection is blocked
- `activate-lark`: bring Feishu/Lark to foreground before validating

Default to `validate-only` unless the decision to send is already made.

## macOS Launcher

The repo mirror keeps the macOS shell launcher for parity with the live skill:

```bash
skill-center/skills/hermes-feishu-operator/scripts/send-hermes-feishu-prompt.sh \
  --expected-chat hermes_agent_mac_mini \
  --validate-only
```

Send after validation with:

```bash
printf '%s' "$PROMPT" | skill-center/skills/hermes-feishu-operator/scripts/send-hermes-feishu-prompt.sh \
  --expected-chat hermes_agent_mac_mini \
  --activate-lark \
  --visual-confirmed \
  --message-stdin \
  --send
```

If GUI sending fails with `osascript` accessibility errors, grant `/usr/bin/osascript` access in `System Settings -> Privacy & Security -> Accessibility`, then rerun `--validate-only`.

## Windows PowerShell Launcher

Use the bundled PowerShell launcher when the skill mirror is synced onto a Windows machine:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/hermes-feishu-operator/scripts/send-hermes-feishu-prompt.ps1 -ExpectedChat hermes_agent_mac_mini -ValidateOnly
```

Send after validation with:

```powershell
$prompt | powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/hermes-feishu-operator/scripts/send-hermes-feishu-prompt.ps1 -ExpectedChat hermes_agent_mac_mini -ActivateLark -VisualConfirmed -MessageStdin -Send
```

Windows behavior notes:

- Run it from Windows PowerShell or `pwsh -STA` so clipboard and `SendKeys` stay available.
- The launcher validates the foreground process as `Lark` or `Feishu`, then checks the main window title for `hermes_agent_mac_mini` unless `-VisualConfirmed` is already set.
- For paste/send it mirrors the macOS flow: click near the bottom-center composer area, use `Ctrl+A` plus Backspace to clear, paste with `Ctrl+V`, then click the visible send button near the bottom-right of the verified window.
- If the Windows title bar does not expose the bot name but the chat is visually confirmed in a fresh screenshot, rerun with `-VisualConfirmed`.
- If focus or click automation is blocked by corporate desktop policy, stop and provide the prompt for manual sending instead of guessing.

## Safety Reminder

This launcher is for safe, narrow Hermes intervention only. It is not a general desktop macro:

- do not bypass the expected-chat check
- do not send a blank message
- do not stack multiple prompts without re-reading local Hermes state
- do not use it to trigger real publishing or file changes outside the authorized scope
