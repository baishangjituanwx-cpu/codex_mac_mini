---
name: "data-review"
description: "Run a post-publish multi-platform content review across 视频号、抖音、快手、B站、微博、百家号、知乎、头条号. Use when Codex needs to collect visible first-wave metrics, compare video and article outcomes, diagnose hook, title, cover, content, account, and route issues, decide Keep, Cut, or Retest, and produce next-day optimization actions."
---

# 数据复盘

This skill turns post-publish data into an actionable review.

Use it to answer:

- what actually happened on each platform
- whether the problem was topic, packaging, account state, or execution
- whether the current conclusion is backed by creator-center verification, public-page verification, or still unverified
- what to keep, cut, or retest tomorrow
- how to compress the review into a Feishu rich-text push for stakeholders
- how the current post compares against the same account's recent published history
- whether the account itself is warming up, unstable, throttled, or format-mismatched

## Use this skill when

- the user asks for 发布后数据复盘, 多平台复盘, 8 平台复盘, or 内容效果分析
- the user wants to compare one topic across multiple creator platforms
- the user wants a reusable nightly review flow or automation prompt
- the user wants next-day title, cover, hook, or topic optimization after publishing
- the user wants to separate content weakness from moderation, login, or publish-route failures
- the user wants the review pushed to a Feishu chat after completion
- the user wants 最近几条视频 or 最近几篇图文的连续对比
- the user wants a 平台账号维度, 账号盘面, or 趋势型数据分析
- the user wants to update the 8-platform Docker dashboard or export the review into a fixed dashboard data contract

## Scope and inputs

Default scope:

- review the user's local "today" and restate it as an exact date in the output
- include content that was published, submitted, duplicate-skipped, blocked, under review, or missing for that date
- unless the user narrows it, expand beyond the single batch and compare against each platform account's recent relevant history
- default historical window: the current batch plus the last 3 to 7 comparable published items on the same platform and format
- if enough evidence exists, prefer a rolling 7-day or 30-day account view over a one-post judgment
- if the platform backend is accessible, do not finalize a strong judgment before checking both:
- the current batch's content row
- the account's creator-center or data-center state
- if the same-format content list is visible, scan all visible published items in that list before calling the current item "best" or "worst"

Start from the strongest available evidence, in this order:

1. platform management list or creator-center page
2. publish logs under `content-library/logs/`
3. source packages under `content-library/posts/`
4. generated assets under `content-library/assets/generated/`
5. comments, DMs, and any midday interaction notes
6. MEMORY or dated notes if the workspace or automation provides them

In this workspace, look first in:

- `content-library/logs/<platform>/`
- `content-library/posts/video/`
- `content-library/posts/baijiahao/`
- `content-library/posts/toutiao/`
- `content-library/posts/weibo/`
- `content-library/posts/zhihu/`
- `content-library/assets/generated/<date-topic>/`
- any dated review notes that reveal platform/account carry-over effects

When the user wants to update the LAN Docker dashboard, also read:

- [docker-dashboard-contract.md](./references/docker-dashboard-contract.md)
- [dashboard-export-template.json](./references/dashboard-export-template.json)

When browser checks are required, route through:

- `platform-ops-hub` for platform routing
- `social-publish-automation` for management-page verification
- `dachen-founder-flywheel` if the review belongs to 大陈's founder-IP loop

## Workflow

1. Define the review set:
- state the exact date, topic, and content package
- list the platforms and formats that were supposed to go out
- separate `published`, `duplicate-skipped`, `blocked`, `under review`, and `not found`
- define the comparison window for each platform account: current batch only, last 3 posts, last 7 days, or last 30 days
- if the target is the 8-platform Docker dashboard, force one explicit platform block for 视频号、抖音、快手、B站、微博、百家号、知乎、头条号 even when some are `not found` or `未完成内容级核验`

2. Collect raw evidence:
- capture exact visible metrics with exact labels
- record publish state such as `已发布`, `审核中`, `草稿`, `不可见`, or `无数据`
- copy down only the highest-value comments or DMs
- pull the strongest available evidence not only for the current item but also for recent comparable items on the same account
- when possible, capture recurring account signals: repeated low distribution, delayed recommendation, moderation lag, or unstable entry rates
- capture an explicit verification grade for each platform:
- `后台已核验`
- `公开页已核验`
- `未完成内容级核验`
- when the account content list is accessible, review all currently visible same-format published rows before writing the platform conclusion
- when the target is the Docker dashboard, also collect or derive the exact card fields the dashboard needs: `latestTitle`, `publishTime`, `contentType`, one numeric `primaryValue`, one comparison baseline, `今日 / 近7日账号 / 近30日账号` three windows, four compact metrics, one short `diagnosis`, and one short `action`
- when writing a companion JSON export, start from [dashboard-export-template.json](./references/dashboard-export-template.json) so all 8 cards and all fixed fields stay present

3. Read the numbers in layers:
- publish success: did the content actually land
- distribution: did the platform give it reach or impressions
- click or open: did title or cover earn entry
- consumption: did users keep watching or reading
- interaction quality: were comments shallow, skeptical, trusting, or conversion-intent
- operational health: did moderation, permissions, or login state distort the result
- account baseline: is this item above, near, or below the account's recent normal band
- account trend: is the platform account warming up, flattening, or weakening over recent posts
- verification completeness: is this a backend-backed conclusion or only a partial/public-page conclusion

4. Diagnose the main cause:
- use [platform-metrics.md](./references/platform-metrics.md) for what to collect
- use [account-slice-analysis.md](./references/account-slice-analysis.md) for recent-post and account-level comparison
- use [diagnosis-and-decisions.md](./references/diagnosis-and-decisions.md) to separate hook, title, cover, structure, account-state, and route failures
- do not flatten every failure into "content weak"
- do not flatten repeated weak distribution into one-post bad luck if the same account has shown the same pattern across several recent items
- when exporting to the Docker dashboard, derive one CSS-safe `status` from the supported set `steady`, `watch`, `warning`, `weak`, `opportunity`, then write a Chinese `statusLabel` that stays grounded in the verified evidence

5. Decide the next move:
- choose `Keep`, `Cut`, or `Retest`
- name the exact variable to change next; avoid vague advice like "optimize content"
- if the problem is account-level, name the account action separately from the content action: for example `keep topic, reduce posting frequency`, `keep platform but switch format`, or `repair route before retest`

6. Produce tomorrow's package:
- one preferred main topic
- one backup topic
- revised title directions
- revised cover-theme directions
- revised hook direction for the next 30-second video
- whether tomorrow should lean more into video, article, or both
- which platforms should continue, pause, or only monitor based on account-state
- whether tomorrow should prioritize fresh distribution tests or account repair / verification
- one `下一批图文内容高占比倾向`
- one `下一批小云雀视频高占比倾向`
- when the target is the Docker dashboard, also produce the board-level fields `title`, `dateLabel`, `subtitle`, `northStar`, exactly 4 `summary` tiles, exactly 3 `keep` items, exactly 3 `cut` items, and exactly 3 `next` items

7. Write back reusable lessons:
- repeated objections
- lead-signal patterns
- platform-specific blocker patterns
- winning hook, title, or cover patterns
- account-level patterns: platform warming, account fatigue, moderation drag, or route instability

8. Sync to Feishu when requested:
- if the user provides a target Feishu `chatId`, use that exact chat
- otherwise, if the workspace has a default notify chat in `.bridge.env`, reuse that target
- Feishu push must be Chinese only
- default Feishu structure is:
- one `总览` message first
- then one `各平台详细状态` message for every checked platform
- if needed, one final `下一批图文 + 小云雀方向` message
- the overview message must include:
- review date and batch
- core judgment
- best / weakest / blocked platforms
- keep / cut / retest summary
- tomorrow's core content direction
- every platform-detail message must include:
- platform name
- verification grade
- current content title or identifier
- publish state
- current visible metrics
- account-state judgment
- recent comparable items or recent baseline
- diagnosis
- next action
- `Keep / Cut / Retest`
- prefer `lark-cli im +messages-send --as bot --chat-id <chatId> --markdown ...` because it reliably renders as a Feishu rich-text post
- confirm success with the returned `message_id`

## Review rules

- Use raw visible numbers first. Do not invent hidden metrics.
- Distinguish `0`, `not visible`, `not yet available`, and `blocked`.
- Compare like with like before cross-platform judging. A 知乎 answer and a 抖音 short video do not win in the same way.
- A post stuck in moderation or hidden by account-state is an operations issue first.
- One strong repeated objection or DM intent signal can outweigh vanity metrics.
- If the data window is too early, say so explicitly and favor `Retest` or `wait for more data`.
- When a platform only exposes partial metrics, diagnose only from what is visible.
- When the same topic works on one platform and fails on another, test packaging and platform fit before killing the topic.
- Prefer management-list verification over editor-page success claims.
- If backend verification is incomplete, write `未完成内容级核验` and do not pretend to have a final content diagnosis.
- Do not call a platform weak until you have checked both the current batch row and the visible account data-center state when that state is accessible.
- When pushing to Feishu, keep the message stakeholder-readable, but never compress away the platform detail block the user explicitly requested.
- When pushing an ops-grade Feishu review, include concrete platform data, account context, and verification grade instead of only high-level conclusions.
- If a metric label is not visible but raw numbers are visible, say that explicitly instead of inventing the label.
- When doing account-level analysis, compare like with like: video vs video, article vs article, and similar time windows first.
- If the account history is too sparse, say `insufficient account history` instead of pretending to see a trend.
- Repeated `审核中`, repeated `0`, or repeated route breakage across recent posts should be treated as account or operations evidence, not isolated accidents.
- If one post is weak but the previous few were normal, favor a single-post packaging diagnosis before calling account decline.
- Every final review must include:
- `下一批图文内容高占比倾向`
- `下一批小云雀视频高占比倾向`
- `未完成核验项`
- before the first real dashboard sync on a device, run `node scripts/dashboard-doctor.js --review-date YYYY-MM-DD`
- if the repo includes `scripts/dashboard-sync-review.js`, prefer that single command over manual export + upload steps
- if the operator wants a wrapper entry, use `bash scripts/dashboard-sync.sh --review-date YYYY-MM-DD` on macOS / Linux or `.\scripts\dashboard-sync.ps1 --review-date YYYY-MM-DD` on Windows
- if the device is only checking field mapping or preparing a handoff, stop after export + validate; do not upload test data into the remote dashboard
- if the device only uses the browser binding flow, do not configure `.env.dashboard` and do not distribute admin credentials; the admin must generate a one-time `设备接入码` in `8081`, and the operator must bind the device from `8080`
- only when the device will run the repo upload scripts, configure `.env.dashboard` or `.env.dashboard.local` in the repo root; required keys are `DASHBOARD_API_BASE`, `DASHBOARD_ACCOUNT_NAME`, `DASHBOARD_ADMIN_USERNAME`, and `DASHBOARD_ADMIN_PASSWORD`
- if the device uses neither `workflow/content-library` nor `content-library`, set `CONTENT_LIBRARY_ROOT`
- If the user asks to update the 8-platform Docker dashboard, append the Docker dashboard mapping block defined in [docker-dashboard-contract.md](./references/docker-dashboard-contract.md), or write the same object to a companion JSON export file when the workflow needs a file-based handoff.
- When exporting to the Docker dashboard, never omit a platform card; keep the card and mark gaps as `未完成内容级核验`, `暂未可见`, or numeric `0` according to the contract.
- When exporting to the Docker dashboard, `primaryValue` must stay numeric so the ranking and ring chart do not break.

## Output format

Always use the fixed structure in [report-template.md](./references/report-template.md).

If the user asks for Feishu同步, keep the main Codex output in the fixed report structure, then send a compressed Feishu-rich-text version to the requested chat.

For metrics vocabulary and platform-specific priorities, read [platform-metrics.md](./references/platform-metrics.md).
For recent-post and account-slice comparison, read [account-slice-analysis.md](./references/account-slice-analysis.md).
For diagnosis and `Keep / Cut / Retest`, read [diagnosis-and-decisions.md](./references/diagnosis-and-decisions.md).
When the review must feed the Docker dashboard, also read [docker-dashboard-contract.md](./references/docker-dashboard-contract.md).
When the review must write a companion JSON file, also use [dashboard-export-template.json](./references/dashboard-export-template.json) as the starting structure.

For first-time device setup of the dashboard chain, also read [docs/dashboard-sync-runbook.md](/Users/baishangjituan/Documents/New%20project/github-ready/multi-platform-content-pipeline/docs/dashboard-sync-runbook.md) and [docs/dashboard-upload-api-contract.md](/Users/baishangjituan/Documents/New%20project/github-ready/multi-platform-content-pipeline/docs/dashboard-upload-api-contract.md).
