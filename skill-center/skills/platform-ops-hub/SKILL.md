---
name: platform-ops-hub
description: Route new-media operations across 微博、百家号、知乎、今日头条 / 头条号、抖音、小红书、微信视频号、快手. Use when Codex needs to decide which platform skill to invoke for publishing, data analysis, comment interaction, rule research, or content optimization, or when the user wants one command surface for multi-platform operations.
---

# Platform Ops Hub

## Overview

Use this skill as the unified entry point for multi-platform new-media operations.

This skill does not replace the platform-specific skills. It decides which one to use, when to combine them, and when browser execution should also load `$social-publish-automation`.

## Supported Platforms

- 微博 -> `$weibo-ops`
- 百家号 -> `$baijiahao-ops`
- 知乎 -> `$zhihu-ops`
- 今日头条 / 头条号 -> `$toutiao-ops`
- 抖音 -> `$douyin-ops`
- 小红书 -> `$xiaohongshu-ops`
- 微信视频号 -> `$wechat-channels-ops`
- 快手 -> `$kuaishou-ops`

## Supported Job Types

- 发布
- 数据分析 / 复盘
- 评论互动 / 社群回应
- 平台规则研究
- 素材内容优化建议
- 封面优化 / 封面修复

## Routing Workflow

### 1. Identify the platform set

- If the user names one platform, load only that platform skill.
- If the user names multiple platforms, load only those platform skills.
- If the user says `全平台`, `多平台`, or uses a campaign-style request, route only to the platforms that are actually in scope instead of loading every platform by default.

### 2. Identify the work type

- `发布` or `补发`:
- load the target platform skill
- if browser-side execution is required, also load `$social-publish-automation`
- if the platform is 今日头条 / 头条号 and the task is rule-heavy, also consult `$toutiao-publish`
- `数据分析`, `复盘`, `看数据`:
- load the target platform skill only
- compare content structure, traffic shape, interaction quality, and account-state implications
- `评论互动`, `回评论`, `私信/留言处理`:
- load the target platform skill only
- prefer operational guidance over generic copywriting
- `规则`, `规范`, `会不会违规`, `权限为什么没有`:
- load the target platform skill only
- use official references first, then local operating notes
- `优化`, `改标题`, `改封面`, `改文案`, `改脚本`:
- if the task is mainly about `封面`, `题图`, `首图`, `缩略图`, `分享卡片`, or post-upload cover editing, load `$platform-cover-ops` first
- add the target platform skill only when the work also needs broader platform context
- optimize for that platform's native distribution and moderation logic

### 3. Decide whether this is comparison or execution

- If the user wants a cross-platform comparison, synthesize the platform-specific recommendations into one answer without flattening the differences.
- If the user wants actual publishing or troubleshooting, keep the execution path platform-specific and load `$social-publish-automation` only for the platforms that require browser work.

### 4. Output shape

- For one platform: give a platform-native answer and keep references to the selected child skill.
- For multiple platforms: group by platform, then by task.
- For campaign work: preserve shared assets, but adapt titles, hooks, interaction strategy, and compliance advice per platform.

## Fast Routing Hints

- Trust-heavy long-form argument -> prefer `$zhihu-ops`
- Search and long-tail intent -> prefer `$baijiahao-ops`
- News-feed article ops with 首发/收益 considerations -> prefer `$toutiao-ops`
- Public hot-topic and interaction-heavy short posts -> prefer `$weibo-ops`
- Short-video packaging and rapid vertical iteration -> prefer `$douyin-ops` or `$kuaishou-ops`
- Lifestyle note packaging and save/share intent -> prefer `$xiaohongshu-ops`
- WeChat-ecosystem distribution and operator-role workflows -> prefer `$wechat-channels-ops`

## Execution Rule

- Use this hub for routing.
- Use the child platform skill for actual operational guidance.
- Use `$social-publish-automation` only when browser-side publishing, resume, or troubleshooting is actually required.

## Publish Notify Rule

- For any multi-platform `发布`, `补发`, or campaign-style execution, require a per-platform Feishu notification after each platform reaches a verified success state.
- The fixed notify target on this machine is chatId `oc_45f4f2c2f0a783f636969cd821179f40`.
- Treat the following as notify-worthy success states only after verification, not immediately after the click:
- `已发布`
- `提交成功`
- `已提交`
- `审核中` when the management list or success page shows the new item has landed
- Notify one platform at a time. Do not bundle multiple platforms into one Feishu message unless the user explicitly asks for a summary.
- The notification should at minimum include:
- platform name
- title or asset identifier
- current platform state
- verification time
- optional public URL or backend URL when useful
- Route the actual send step through `$social-publish-automation` so the routing layer stays thin and the browser execution layer owns the final verification and push.
