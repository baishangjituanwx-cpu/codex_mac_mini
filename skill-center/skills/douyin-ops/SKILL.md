---
name: douyin-ops
description: Operate a 抖音 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to publish or troubleshoot a Douyin post, review creator-center status and performance, handle comments, check current rule or violation signals, or improve hooks, covers, and short-video packaging.
---

# Douyin Ops

## Overview

Use this skill for 抖音日常运营. It covers publishing, review, interaction, rule lookup, and material optimization on one platform.

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Prepare the package before opening the editor: video file, caption, cover, topic tags, and any landing or挂载 needs.
- For browser-side execution, route through `$social-publish-automation`.
- The official platform supports app-side short-video publishing and PC-side publishing through `抖音创作服务平台`.
- Verify from `作品管理` or creator-side list state, not only from the final submit click.
- Treat `审核中` as submitted successfully unless a stronger failure signal appears.

### 2. Data Analysis

- Review from `抖音创作者中心` and creator-management surfaces where available.
- Track at least:
- publish status and入库情况
- interaction quality in comments
- follower movement
- whether the content belongs to a stable vertical
- account status, effective-fan, and recent violation state when the task involves tags or commercialization
- Use weak-video reviews to separate packaging problems from account-state or rule problems.

### 3. Comment Interaction

- Reply early to useful questions, buying-intent comments, and requests for clarification.
- Do not waste time on obvious bait, abuse, or spam.
- Fold recurring user questions into later scripts, captions, or pinned comment plans.
- Treat comment quality as part of content quality, not only customer service.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before relying on a tag, commercialization flow, or cross-platform distribution assumption.
- Priority rule surfaces:
- current account violation state
- real-name and adult-status requirements when a capability depends on them
- tag or挂载 eligibility
- content originality and low-quality repetition risk
- If a capability is denied, confirm whether the issue is account-state, eligibility threshold, or content quality before rewriting assets.

### 5. Material Optimization Suggestions

- Improve weak material in this order:
- stronger first 1 to 3 seconds
- clearer cover and caption framing
- tighter single-topic positioning
- better proof, demo, or result visibility
- cleaner CTA and comment prompt
- For repeatable growth, prefer a stable vertical, consistent packaging, and real interaction over random topic switching.

## Local Notes

- In this workspace, 抖音上传和提交本身较顺，主要问题是发布后要继续核作品管理页是否真正入库。
- `审核中` 应视为已提交，而不是失败。
- In this workspace's founder-IP workflow, once 小云雀 has generated the video, the default next step is to build one prepared `3:4` cover and one prepared `4:3` cover with one 8 to 10 Chinese-character theme, then upload those local covers instead of using 抖音默认帧 or `AI封面`.
- Keep credentials, SMS codes, and recovery details out of notes and artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official publish and eligibility references plus local operating notes.
