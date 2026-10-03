---
name: toutiao-publish
description: Focused reference for 今日头条 / 头条号图文 workflow, monetization, 首发, and edit-limit rules. Use when Codex needs the official entry paths, login and phone-verification rules, ad monetization settings, 首发 eligibility, or article maintenance limits. For browser-side execution, prefer $social-publish-automation.
---

# Toutiao Publish

## Overview

Use this skill as the focused 今日头条 / 头条号图文 rulebook. It packages the official help-center workflow plus local operational notes for policy lookup and publish planning.

Browser execution for 头条号发布 is now handled by `$social-publish-automation`. Use this skill when the task is mainly about entry paths, login rules, ad monetization, 首发 eligibility, edit limits, or policy interpretation.

## Before You Touch The UI

- Confirm the target is 图文, not a video or micro-post flow.
- Gather the publish package first: title, body, images, source attribution, and any external or internal links.
- Decide up front whether the post should use `投放广告赚收益` and whether it is eligible for `头条首发`.
- Read [references/toutiao-publish-notes.md](references/toutiao-publish-notes.md) before making policy or monetization choices.

## Workflow

### 1. Pick the correct publish entry

- PC manual publishing: log into the creator backend, then go to `主页 -> 创作 -> 图文`.
- Mobile manual publishing: use either `今日头条 APP -> 首页右上角发布按钮 -> 写文章` or `今日头条 APP -> 我的 -> 创作中心 -> 发布 -> 写文章`.
- If the user wants mirrored publication from another source of truth, evaluate whether `内容源同步` is the better path than manual reposting.

### 2. Clear login and security gates first

- Prefer an already-valid creator session.
- On desktop, the official login methods are SMS code, account password, or an authorized 抖音 login.
- Treat SMS verification, captcha, or login safety checks as manual checkpoints, not automation bugs.
- Important platform rule: if the account has not logged in on the current device and browser with SMS verification within the last 30 days, login or publish-time verification can be triggered.

### 3. Publish with realistic editor interaction

- Use real typing or stable editor actions when browser automation is involved; do not assume raw DOM assignment will activate validation.
- Re-read the page after writing title and body instead of trusting the input call.
- If monetization is desired and the account has the right enabled, turn on `投放广告赚收益` in the publish settings.
- Only enable `头条首发` when the article is truly original, has more than 100 Chinese characters of正文, and will stay exclusive to 头条 for 72 hours.

### 4. Verify the result outside the publish button

- Confirm the outcome from `作品管理`, a visible success message, or a public article URL.
- Distinguish these states clearly: request sent but unconfirmed, submitted and awaiting review, published and publicly visible, or still blocked on login, verification, or invalid form state.

### 5. Maintain the article correctly

- Modification path: PC uses `管理 -> 作品管理 -> 文章 -> 修改`; mobile uses `我的 -> 创作中心 -> 找到文章 -> ... -> 修改`.
- Official limit: each article supports at most 5 edits.
- Articles older than 14 days, or articles already restricted for rule issues, cannot be edited in place.
- Frequent delete, modify, or duplicate publication behavior can hurt recommendation.
- Withdrawal and deletion should be done from the article management view, not by creating a replacement copy first.

## Guardrails

- Do not label a post as `头条首发` if it is adapted from another live post, assembled from public information, or intended for same-day cross-posting elsewhere.
- Treat clickbait, rumors, vulgarity, fake claims, misleading product promises, and low-quality templated copy as high-risk. These can cost credit points and distribution.
- The current credit system starts at 100. Violations can deduct 10 to 70 points, and a score of 0 leads to account closure.
- If the user is publishing promotional or product content, watch closely for exaggerated claims and unsupported superlatives such as `最`, `第一`, or guaranteed outcomes.
- When asked about rules, monetization, or首发 eligibility, prefer the official summaries in [references/toutiao-publish-notes.md](references/toutiao-publish-notes.md) over memory alone.

## Local Operating Notes

- In this workspace, the most recent 今日头条 blocker was missing creator login state on desktop. The flow stayed on the verification-code login page, and switching to password login did not reliably expose the password form.
- Treat that specific state as a session problem first, not as a broken draft.
- Keep credentials and verification codes out of notes, memory files, screenshots, and skill references.

## Reference File

- Use [references/toutiao-publish-notes.md](references/toutiao-publish-notes.md) for the distilled official workflow, monetization rules, 首发 requirements, and source links.
