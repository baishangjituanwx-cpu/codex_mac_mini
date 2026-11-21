---
name: wechat-moments-desktop-ops
description: Use this skill when the user wants to verify whether Mac WeChat supports posting Moments, learn the desktop posting workflow, troubleshoot why the Moments entry or publish button is missing, check version-dependent Moments features, or prepare to operate Moments from the macOS WeChat desktop client.
---

# WeChat Moments Desktop Ops

## Overview

Use this skill for Mac WeChat desktop Moments work: confirming whether the installed version supports posting, following the desktop publish flow, understanding version-dependent features, and troubleshooting why the Moments entry or publish control is missing. Keep the primary evidence in `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/official-notes.md` and the step-by-step operational guidance in `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/desktop-posting-guide.md`.

## Quick Start

1. Check the installed Mac WeChat version:
   ```bash
   python3 /Users/z/.codex/skills/wechat-moments-desktop-ops/scripts/check_wechat_moments_support.py
   ```
2. Read the evidence summary:
   - `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/official-notes.md`
3. Follow the desktop posting flow:
   - `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/desktop-posting-guide.md`

## What This Skill Should Answer

- Does Mac WeChat support posting Moments at all
- Which versions are known to support Moments posting
- Where the Moments entry is in desktop WeChat
- How to publish text, images, or video from Mac WeChat
- Which newer Moments features are version-dependent
- What to do when the entry exists but posting fails or the page looks different

## Workflow

### 1. Verify support and version

Run:

```bash
python3 /Users/z/.codex/skills/wechat-moments-desktop-ops/scripts/check_wechat_moments_support.py
```

Interpretation:

- `3.1.1` and later should be treated as the safe baseline for Mac desktop Moments publishing, based on public reporting of the official 3.1.1 release.
- `4.0.6` and later add newer Moments capabilities called out in the App Store release history.
- `4.1.4` and later add richer Moments comment interactions called out in the App Store release history.

### 2. Confirm the desktop posting path

Use the guide in `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/desktop-posting-guide.md`.

Key principle:

- Distinguish direct evidence from inference.
- The existence of Moments support on Mac is supported by source evidence.
- The exact modern publish path on current Mac desktop is inferred from the unified desktop UI and widely reported desktop flow. State that clearly when answering.

### 3. Troubleshoot missing entry or missing publish controls

Check these in order:

1. Is the app really `WeChat` on macOS, not a different desktop client.
2. Is the installed version current enough.
3. Is the user signed into the correct account.
4. Does the left sidebar show the Moments entry.
5. If the sidebar entry exists but the compose control is missing, compare against version-dependent behavior in the references.

### 4. Explain limits carefully

Do not overclaim support for specific privacy controls, scheduling, bulk posting, or draft management unless you have a source or a direct local verification for that exact behavior.

## Practical Rules

- Prefer the Mac App Store page as the source of truth for current release history and compatibility.
- Use secondary sources only to fill gaps the official page does not spell out, such as when Mac Moments posting first appeared.
- When citing the current UI path, label it as an inference if the source chain does not explicitly show the current Mac screen.
- If the user wants automation, first verify the current desktop UI path manually before attempting any UI scripting.

## Reference Files

- `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/official-notes.md`
- `/Users/z/.codex/skills/wechat-moments-desktop-ops/references/desktop-posting-guide.md`
- `/Users/z/.codex/skills/wechat-moments-desktop-ops/scripts/check_wechat_moments_support.py`
