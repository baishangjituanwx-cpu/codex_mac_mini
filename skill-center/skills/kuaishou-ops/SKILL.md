---
name: kuaishou-ops
description: Operate a 快手 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to publish or troubleshoot through 快手创作者服务平台, review works and interaction quality, handle comments, check current community and reporting rules, or improve short-video packaging for better completion and response.
---

# Kuaishou Ops

## Overview

Use this skill for 快手日常运营. It covers publish execution, postmortem review, interaction handling, rule lookup, and packaging advice.

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Prepare the package first: video, title, description, cover, tags, and expected CTA.
- For browser-side publishing or troubleshooting, route through `$social-publish-automation`.
- Prefer Chrome DevTools / CDP-attached control for Kuaishou page inspection, file input handling, and publish-status verification when it can attach to the existing logged-in Chrome session.
- If the logged-in Kuaishou tab is only available in a normal Chrome profile without a CDP port, keep OpenCLI / Browser Bridge as the safe fallback instead of restarting Chrome and risking session loss.
- On a Windows repo mirror, first check the existing session with `Invoke-WebRequest http://127.0.0.1:9222/json/version` or `.\scripts\social-publisher.ps1 doctor --package <yaml> --platform kuaishou --check-browser`; only start a new browser through `.\scripts\start-chrome-cdp.ps1` when there is no safe logged-in CDP session to reuse.
- Use `快手创作者服务平台` as the main desktop surface when operating from the web.
- Verify from `作品管理`, not only from the submit action.
- Treat `审核中` as the normal success-adjacent terminal state after submit.

### 2. Data Analysis

- Review from creator-side works and data surfaces where available.
- Track at least:
- publish status and list presence
- interaction quality in comments
- follower movement
- whether the opening and packaging fit the real topic
- repeatable performance by series or format
- Use postmortems to identify whether weak performance came from weak opening, weak clarity, or low community fit.

### 3. Comment Interaction

- Reply quickly to genuine questions, purchase-intent questions, and requests for detail.
- Report or ignore obviously harmful, abusive, or spammy comments instead of feeding them.
- Treat comment themes as input for later scripts, pinned comments, or revised hooks.
- Keep replies direct and human; over-polished brand language usually weakens trust.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before posting risky or promotional material.
- Priority checks:
- current community norms
- available creator-service surface
- whether the content risks triggering reportable categories such as fraud, rumor, vulgarity, or harmful behavior
- If a post is blocked or heavily limited, compare the package against community norms before resubmitting.

### 5. Material Optimization Suggestions

- Improve weak material in this order:
- stronger opening shot
- clearer spoken or captioned value
- tighter cover-title match
- more direct scenario or result
- cleaner CTA and comment prompt
- Optimize for completion, clarity, and trust rather than trying to sound over-produced.

## Local Notes

- In this workspace, 快手的稳定经验是：
- initial upload may land in an editable draft, and the draft-resume path is workable
- final verification should happen in `作品管理`
- `审核中` is the expected post-submit state
- for larger local videos, page-side CDP `DOM.setFileInputFiles` was more stable than ordinary remote `setInputFiles`
- the verified description editor node was `#work-description-edit`
- the effective submit control was the bottom action area containing `发布 / 取消`
- 2026-04-29 operator preference: for upcoming Kuaishou publishing, try Chrome DevTools / CDP first when it is already available; do not restart the logged-in browser just to enable CDP without explicit confirmation.
- If Windows has to fall back to the native chooser, first copy the real asset to a short non-symlink `%TEMP%\\<simple-name>` path, use that exact file path in the chooser's file-name box, then verify the accepted upload from `作品管理` rather than trusting the chooser close event.
- In this workspace's founder-IP workflow, once 小云雀 has generated the video, the default next step is to build prepared vertical and horizontal covers carrying one 8 to 10 Chinese-character theme, and upload the prepared cover instead of relying on default frame or `智能推荐封面`.
- Keep credentials, verification codes, and private account details out of notes and artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official creator-platform references and local publish lessons.
