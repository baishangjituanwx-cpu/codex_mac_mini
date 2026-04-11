---
name: "data-review"
description: "Run a post-publish multi-platform content review across 视频号、抖音、快手、B站、微博、百家号、知乎、头条号. Use when Codex needs to collect visible first-wave metrics, compare video and article outcomes, diagnose hook, title, cover, content, account, and route issues, decide Keep, Cut, or Retest, and produce next-day optimization actions."
---

# 数据复盘

This skill turns post-publish data into an actionable review.

Use it to answer:

- what actually happened on each platform
- whether the problem was topic, packaging, account state, or execution
- what to keep, cut, or retest tomorrow

## Use this skill when

- the user asks for 发布后数据复盘, 多平台复盘, 8 平台复盘, or 内容效果分析
- the user wants to compare one topic across multiple creator platforms
- the user wants a reusable nightly review flow or automation prompt
- the user wants next-day title, cover, hook, or topic optimization after publishing
- the user wants to separate content weakness from moderation, login, or publish-route failures

## Scope and inputs

Default scope:

- review the user's local "today" and restate it as an exact date in the output
- include content that was published, submitted, duplicate-skipped, blocked, under review, or missing for that date

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

When browser checks are required, route through:

- `platform-ops-hub` for platform routing
- `social-publish-automation` for management-page verification
- `dachen-founder-flywheel` if the review belongs to 大陈's founder-IP loop

## Workflow

1. Define the review set:
- state the exact date, topic, and content package
- list the platforms and formats that were supposed to go out
- separate `published`, `duplicate-skipped`, `blocked`, `under review`, and `not found`

2. Collect raw evidence:
- capture exact visible metrics with exact labels
- record publish state such as `已发布`, `审核中`, `草稿`, `不可见`, or `无数据`
- copy down only the highest-value comments or DMs

3. Read the numbers in layers:
- publish success: did the content actually land
- distribution: did the platform give it reach or impressions
- click or open: did title or cover earn entry
- consumption: did users keep watching or reading
- interaction quality: were comments shallow, skeptical, trusting, or conversion-intent
- operational health: did moderation, permissions, or login state distort the result

4. Diagnose the main cause:
- use [platform-metrics.md](./references/platform-metrics.md) for what to collect
- use [diagnosis-and-decisions.md](./references/diagnosis-and-decisions.md) to separate hook, title, cover, structure, account-state, and route failures
- do not flatten every failure into "content weak"

5. Decide the next move:
- choose `Keep`, `Cut`, or `Retest`
- name the exact variable to change next; avoid vague advice like "optimize content"

6. Produce tomorrow's package:
- one preferred main topic
- one backup topic
- revised title directions
- revised cover-theme directions
- revised hook direction for the next 30-second video
- whether tomorrow should lean more into video, article, or both

7. Write back reusable lessons:
- repeated objections
- lead-signal patterns
- platform-specific blocker patterns
- winning hook, title, or cover patterns

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

## Output format

Always use the fixed structure in [report-template.md](./references/report-template.md).

For metrics vocabulary and platform-specific priorities, read [platform-metrics.md](./references/platform-metrics.md).
For diagnosis and `Keep / Cut / Retest`, read [diagnosis-and-decisions.md](./references/diagnosis-and-decisions.md).
