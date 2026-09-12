---
name: baijiahao-ops
description: Operate a 百家号 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to post or troubleshoot 图文 on 百家号, review works, fan, or income analysis, handle comments or private-message feedback, study current content-audit rules, or improve titles, covers, and content packaging for Baidu distribution.
---

# Baijiahao Ops

## Overview

Use this skill for 百家号日常运营. It combines platform-side publishing, data review, interaction handling, rule research, and optimization guidance in one place.

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Confirm the content type first. 百家号 officially supports 图文、动态、视频、图集、直播 and related creator-management flows.
- Build the package before opening the editor: title, cover, body, source attribution, and expected distribution goal.
- Because 百家号 content can be distributed across 百度 App, 好看视频, and search, optimize for explicit user intent and clear subject framing before posting.
- Before any retry or补发, check `作品管理` for the exact title first. If the same-day item already exists in `已发布`, `审核中`, or `审核未通过`, treat the task as an idempotency problem before treating it as a publish failure.
- Verify from `作品管理`, not only from the publish button.
- If the platform blocks final submit behind `百度安全验证` or cover-selection issues, treat it as a manual checkpoint rather than a generic automation failure.
- Do not classify `删除` as complete until the confirm dialog is accepted and the list is reloaded without that item.

### 2. Data Analysis

- Use the creator surfaces that expose `作品数据`, `粉丝分析`, and `收益分析`.
- Review content by:
- content type
- recent series or topic cluster
- publish status versus actual distribution
- comment and private-message quality
- income and fan movement if enabled
- When metrics are available, compare posts that get search-like long-tail traction against posts that only spike briefly.

### 3. Comment Interaction

- Use the platform's built-in comment and message management rather than treating interaction as an afterthought.
- The official app description explicitly lists fan comments, follows, likes, favorites, shares, and private messages as creator-management surfaces.
- Reply quickly to recurring product or topic questions, then bucket recurring objections into future article angles.
- Hide, report, or ignore spammy lead-gen bait instead of arguing with it publicly.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before editing titles, covers, or promotional copy.
- The most important rule layer available publicly is the official `百家号素材审核规范`.
- Priority risks:
- title-bait wording
- low-quality or mismatched covers
- fake or unverifiable claims
- obvious promotion or导流
- violent, vulgar, rumor-like, or illegal content
- Keep an eye on account-side `信用分` and `权益申请` in the official creator surfaces.

### 5. Material Optimization Suggestions

- Optimize for usefulness and search clarity first, then for emotional punch.
- Improve weak material in this order:
- make the title precise and readable
- ensure cover and正文 strongly match
- remove external-platform导流
- replace generic claims with proof, examples, or screenshots
- tighten structure around one clear user problem
- If the content is time-sensitive, make freshness obvious. The official audit notes explicitly encourage timely articles.

## Local Notes

- In this workspace, 百家号 has shown two stable blockers:
- final publish can stop at `百度安全验证`
- AI cover generation can return error or undefined previews, leaving `确定` disabled
- A prior successful workaround was local cover upload followed by publish verification in `作品管理`.
- In this workspace's founder-IP workflow, once 小云雀 has generated the upstream content package, 百家号 should default to the prepared local cover instead of AI封图.
- A later failure mode was duplicate same-title submission after a retry. The second copy was marked `审核未通过 / 作品存在违规` even though the first copy had already been accepted.
- The practical rule in this workspace is: `发前先查重，发后不自动重投`.
- Keep credentials, verification codes, and private account details out of notes and artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official capability descriptions, content-audit rules, and local publishing lessons.
