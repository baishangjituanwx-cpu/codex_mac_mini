---
name: wechat-video-channel-share-desktop-ops
description: Use this skill when the user wants to verify whether Mac WeChat can share WeChat Channels posts to chats, groups, or Moments, learn the desktop workflow for forwarding a Channels video, troubleshoot missing share targets or version-dependent behavior, or prepare to operate this flow from the macOS WeChat client.
---

# WeChat Video Channel Share Desktop Ops

## Overview

Use this skill for Mac WeChat desktop work around sharing WeChat Channels posts: checking whether the installed build is new enough, understanding what is directly supported by source evidence versus inference, forwarding a Channels video into group chats, and sending that content to Moments. Keep the evidence summary in `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/official-notes.md` and the operational steps in `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/desktop-share-guide.md`.

## Quick Start

1. Check the installed Mac WeChat version:
   ```bash
   python3 /Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/scripts/check_wechat_video_channel_share_support.py
   ```
2. Read the evidence summary:
   - `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/official-notes.md`
3. Follow the action guide:
   - `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/desktop-share-guide.md`

## What This Skill Should Answer

- Does Mac WeChat support opening WeChat Channels content at all
- Which desktop versions are the relevant public baselines for Moments posting, Channels entry, and Channels-to-Moments sharing
- How to forward a Channels video into one or more group chats from desktop WeChat
- How to share a Channels video to Moments from desktop WeChat
- What to do when the share sheet is missing `群聊`, `转发给朋友`, or `分享到朋友圈`
- What should be treated as direct evidence and what should be treated as inference

## Workflow

### 1. Verify support and version

Run:

```bash
python3 /Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/scripts/check_wechat_video_channel_share_support.py
```

Interpretation:

- `3.1.1` and later should be treated as the safe public baseline for Mac desktop Moments posting.
- `3.3.0` and later should be treated as the public baseline for a native Channels entry in Mac WeChat.
- `3.4.0.2` and later should be treated as the public baseline for sharing public-account articles and Channels content to Moments.
- `4.0.6` and later should be treated as the safer baseline for a more unified Windows and Mac desktop UI.

### 2. Separate the two targets before answering

Use the guide in `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/desktop-share-guide.md`.

There are two different jobs:

- `转发到群聊`: desktop share flow from a Channels post into a selected chat or group
- `发布到朋友圈`: desktop share flow from a Channels post into the Moments composer

Do not mix them. A build can support one part earlier than the other.

### 3. Explain evidence versus inference clearly

Key principle:

- Direct evidence exists for Mac desktop Moments posting and for Mac desktop sharing Channels content to Moments.
- Direct evidence also exists that older Mac builds could open Channels content shared inside chats, and that later Mac builds added a native Channels entry.
- A current desktop route for forwarding a Channels post into group chats is reasonable and often available in practice, but the exact button labels and share-sheet layout should still be treated as live-verification items unless you have the current UI in front of you.

### 4. Troubleshoot missing targets in order

Check these in order:

1. Is the installed version new enough for the target action.
2. Is the left sidebar showing the Channels entry.
3. After opening the video, does the share menu expose `转发给朋友`, `发送给朋友`, `群聊`, or `分享到朋友圈`.
4. If `分享到朋友圈` is missing, compare against the version baselines first, then assume UI drift or account gray release.
5. If chat sharing works but Moments sharing does not, use phone WeChat as the fallback instead of overclaiming desktop support.

### 5. Pair with local-operation skills when needed

If the user wants live desktop operation or automation on this machine, pair this skill with:

- `$wechat-desktop-ops`
- `$wechat-moments-desktop-ops`

This skill is the evidence and workflow layer. Those skills handle the local Mac desktop execution details.

## Practical Rules

- Prefer the Mac App Store page as the current official source of truth for active Mac release history.
- Use public reporting only to fill the gaps that the App Store page does not spell out, such as when Channels entry or Channels-to-Moments sharing first appeared on Mac.
- When you describe the current desktop share path, label it as an inference if the source chain does not show the exact current screen.
- On this machine, current desktop WeChat was live-verified to support selecting more than one group inside the `微信发送给` picker, and the send button changed to `分别发送(n)`.
- In that picker, the top-left field is for recipient search only. Any forwarding note belongs in the bottom-right note box above the green send button.
- If the user asks for automation, manually verify the current share sheet once before scripting it.

## Reference Files

- `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/official-notes.md`
- `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/references/desktop-share-guide.md`
- `/Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/scripts/check_wechat_video_channel_share_support.py`
