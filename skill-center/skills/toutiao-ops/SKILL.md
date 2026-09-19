---
name: toutiao-ops
description: Operate a 今日头条 / 头条号 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to post or repair 视频 or 图文 workflows, review creator and收益 signals, handle comment interaction, research 首发 or credit rules, or improve materials for reach, originality, and compliance on 头条.
---

# Toutiao Ops

## Overview

Use this skill for 今日头条 / 头条号日常运营. It expands beyond pure publishing into review, interaction, rule tracking, and optimization.

If the task is a direct browser publish flow, use `$social-publish-automation`.

## Workflow

### 1. Publish

- Confirm whether the task is 视频发布, manual 图文发布, or `内容源同步`.
- In a Seedance video campaign, default 头条号 to 视频发布 with the generated `mp4`; only use 图文发布 when the user explicitly asks for a 头条图文派生稿.
- Prepare the package first: title, body, images, source attribution, ad setting, and whether `头条首发` is legitimate.
- For concrete browser-side posting steps, defer to `$social-publish-automation`.
- On a Windows repo mirror, keep the same path through `automation/python-platform-takeover`: `.\scripts\social-publisher.ps1 doctor --package <yaml> --platform toutiao --check-browser`, then `inspect-tabs`, then `publish`. Do not invent a second Windows-only article flow for a Seedance video campaign.
- If `receipt-status` or the management page shows `blocked_account_review_pending`, treat that as a real platform blocker rather than a fresh retry signal. On Windows and macOS, keep the receipt, stop the publish loop, and wait for account review to pass or for the user to choose a different account / release plan.
- Verify from `作品管理`, visible success state, or a public article URL rather than trusting the click result alone.

### 2. Data Analysis

- Review creator-side performance through the available `数据` and `收益` views.
- Even when the platform does not expose every metric publicly in help docs, treat these as the main review buckets:
- reading or distribution trend
- comments and user value signals
-收益状态
- whether the post qualified for ad or首发 benefits
- For optimization work, map the content against the quality dimensions the platform explicitly rewards: `时效`, `原创深度`, `信息增量`, `创作规范`, and `用户价值`.

### 3. Comment Interaction

- Check article comments soon after posting and again after the first recommendation window.
- Reply early to factual follow-ups, product or workflow questions, and sincere disagreement.
- Hide, report, or ignore rumor-bait, abuse, and obvious spam rather than feeding it.
- Treat recurring comments as input for follow-up topics, FAQs, or revisions in the next post package.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before posting promotional, news-adjacent, or cross-posted material.
- The highest-risk areas on 头条 are:
- fake or unverifiable claims
- vulgar or rumor-style packaging
- misleading commercial claims
- improper `头条首发` declaration
- low-quality or weakly related images and formatting
- If the user wants 首发 or收益, validate eligibility before publishing instead of fixing it after the fact.

### 5. Material Optimization Suggestions

- Optimize for user value and originality before reach tricks.
- Improve weak materials in this order:
- make the information gain explicit
- tighten title-body relevance
- strengthen proof or firsthand detail
- raise format cleanliness and image relevance
- remove exaggerated or guaranteed claims
- For 首发 candidates, do not optimize by splitting or lightly rewriting an existing post. The platform explicitly treats stitched or pseudo-original content as non-compliant.

## Local Notes

- In this workspace, the main 今日头条 blocker was missing creator login state on desktop, leaving the flow on verification-code login without exposing the password form reliably.
- Treat that state as a session checkpoint first, not as an editor bug.
- In this workspace's founder-IP workflow, once Seedance or 小云雀 has generated the upstream content package, 头条号 should default to the prepared local video and local cover instead of a generic automatic cover.
- On Windows, mirror that same default into the content package and upload matrix with real quoted `C:/...` asset paths. If the package is still missing a video path, cover path, or final video title/description pair, it is not yet ready for 头条号发布.
- Keep credentials, SMS codes, and recovery details out of notes and generated artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official publish,收益,首发,信用分, and local operating notes.
