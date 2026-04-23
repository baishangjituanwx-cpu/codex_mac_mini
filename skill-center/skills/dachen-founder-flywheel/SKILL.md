---
name: dachen-founder-flywheel
description: Run the daily 8-platform founder-IP operating loop for 大陈 as an AI entrepreneur focused on intelligent-agent applications. Use when Codex needs one reusable system for topic planning, platform packaging, publishing priorities, comment and private-message interaction, review, optimization, or daily automation across 微博、百家号、知乎、今日头条 / 头条号、抖音、小红书、微信视频号、快手.
---

# Dachen Founder Flywheel

## Overview

Use this skill as the operating system for 大陈这个 AI 创业者 IP。

It is not a single-platform posting skill. It turns one daily topic into an 8 平台飞轮:

- topic selection
- platform packaging
- publish execution
- comments and private-message handling
- review
- next-day optimization

## Core Positioning

The IP theme is fixed:

- 大陈 = AI 创业者 / 智能体应用实践者
- Main topic = `智能体应用`
- Default narrative = from `会说` to `会做`

The account should feel like:

- a builder, not a generic marketer
- a founder with judgments, not a repost bot
- someone showing how intelligent agents enter real work, not only model talk

## Content Pillars

Use these five pillars and do not let the account drift into random AI news reposting.

### 1. Founder Judgment

- what the market gets wrong about AI tools
- why teams still rework after using AI
- what founders should care about beyond model benchmarks

### 2. Productized Agent Use Cases

- marketing workflow agents
- content production agents
- business coordination agents
- repetitive execution tasks where AI should reduce rework

### 3. Build in Public

- product iterations
- user growth signals
- launch milestones
- founder-level reflections from shipping

### 4. User and Market Proof

- real user questions
- recurring objections
- concrete before and after cases
- early usage patterns and what they imply

### 5. Practical Demos

- what the product actually does
- what is still manual
- where AI still breaks
- why the current workflow is better than pure chat

## Daily Flywheel

### Step 1. Pick one core topic

- Every day starts with one topic, not eight unrelated ideas.
- The topic must come from:
- yesterday's metrics
- recurring comments or DMs
- a product update
- a founder judgment worth repeating

Priority topic shapes:

- `为什么很多团队用了 AI，返工却没有减少`
- `为什么智能体应用比聊天工具更接近真实工作`
- `做 AI 产品时，哪些能力用户真正在意`

### Step 2. Package by platform

- Route through [$platform-ops-hub](/Users/z/.codex/skills/platform-ops-hub/SKILL.md).
- If the main bottleneck is cover or first-frame packaging, also load [$platform-cover-ops](/Users/z/.codex/skills/platform-cover-ops/SKILL.md).
- If browser execution is required, add [$social-publish-automation](/Users/z/.codex/skills/social-publish-automation/SKILL.md).

Platform roles:

- 微博: public opinion, hot takes, early comments
- 百家号: search-intent questions, long-tail reads
- 知乎: trust-building long-form argument
- 头条号: broad feed distribution for business problem framing
- 抖音: hook, pain, short demo
- 小红书: native note packaging, save/share intent
- 视频号: private-domain-friendly founder trust
- 快手: direct practical demo and plain-language reach

### Step 3. Publish in priority order

Default daily execution order:

1. 微博 / 抖音 / 小红书 / 视频号
2. 百家号 / 知乎 / 头条号
3. 快手

Reason:

- short-form surfaces generate faster signal
- long-form surfaces need stronger packaging after the topic is proven
- 快手 follows once the short-video package is stable

Duplicate control:

- Do not treat a shaky browser click as permission to re-post the same platform item.
- Before any retry on the same platform, verify the local publish receipt ledger as well as the creator-side pages.
- Before any retry on the same platform, verify the management list and the public-facing profile or works feed.
- If the same-day item already exists, do not publish a second copy unless the old one has a real structural defect and has already been manually removed or explicitly abandoned.
- For 视频号, do not treat “换了几个词” as a new package if the latest rows still show the same `短标题` and a highly similar正文骨架.
- For 视频号, same `短标题` plus high正文相似度 means `停止发布`, even across different calendar days.
- `表现差` is not a reason to重发.
- `流程没核清楚` is not a reason to重发.
- `标题 / 正文 / 封面 / 视频素材本身错误` is a valid reason to replace, but only after the old item is handled.
- For 小红书, manager lag is not a reason to重发 once `success: true`, `share_link`, or a blocking local receipt already exists.

### Step 4. Handle comments and private messages

- Treat interaction as product research, not after-sales support.
- Sort incoming signals into:
- trust questions
- product understanding gaps
- pricing or conversion intent
- repeated objections
- spam or low-value noise

Action rule:

- reply fast to trust and product questions
- save recurring objections into tomorrow's topic bank
- do not over-engage low-value arguments

### Step 5. Review at end of day

- Compare:
- click-through or first exposure
- comment quality
- whether the same core topic won on one platform and died on another
- whether the weak point was hook, cover, title, or account-state
- route the evening review through [$data-review](/Users/baishangjituan/.codex/skills/data-review/SKILL.md) when the user wants a formal nightly复盘
- do not finalize the nightly judgment before checking:
- all visible published items relevant to the current batch
- the accessible creator-center or data-center state for each platform
- if one platform still lacks content-level verification, keep it in the review as `未完成内容级核验`

Use the review to decide:

- keep
- cut
- retest

### Step 6. Feed tomorrow's optimization

- update the next-day topic queue
- refresh high-performing hooks
- save failed cover and title patterns to avoid repeating them
- write any new operational lesson to memory when it is reusable
- always output one `下一批图文内容高占比倾向`
- always output one `下一批小云雀视频高占比倾向`
- when Feishu sync is requested, send `总览 + 各平台详细状态` in Chinese instead of a single compressed paragraph

## Platform Execution Rules

### 微博

- Use direct founder judgments, not neutral press-release tone.
- Good outcome: comments and quoted disagreement that reveal demand.

### 百家号

- Use question-style titles and concrete utility framing.
- Good outcome: search-like long-tail traction, not only immediate spikes.

### 知乎

- Use argument and evidence.
- Good outcome: fewer reads than feed platforms is acceptable if trust and收藏 improve.

### 头条号

- Use business-problem framing.
- If there are impressions but zero reads, repair title and cover first.

### 抖音

- First 1 to 3 seconds carry the post.
- If the cover is weak, the video is handicapped before playback.

### 小红书

- Native note packaging matters more than “brand awareness” aesthetics.
- Strong saves and high-intent comments matter more than empty views.
- Duplicate prevention must use `本地发布台账 + 笔记管理` together, not either one alone.

### 视频号

- Optimize for trust and shareability.
- Founder credibility and private-domain compatibility matter more here than pure novelty.

### 快手

- Use plain language and practical framing.
- Better to be direct than polished-but-vague.

## Daily Automation Design

Run the flywheel in three daily sweeps instead of one oversized task.

### Morning Sweep

- read yesterday's results
- choose today's one topic
- output publish priorities and platform packages

### Midday Sweep

- check comments, DMs, and interaction signals
- sort reply priorities
- identify repeated objections

### Evening Sweep

- compare platform performance
- decide what to continue, stop, or retest
- update reusable lessons

## Reference Files

- `references/flywheel-operating-system.md`: core founder-IP operating model
- `references/daily-automation-spec.md`: morning, midday, and evening automation contract
- `references/weekly-content-calendar.md`: reusable 7-day topic calendar and 8-platform packaging sequence
- `references/review-scorecard.md`: nightly review rubric, scoring frame, and copy-ready template

When the user asks for a weekly plan, weekly calendar, platform-by-platform daily packaging, or a nightly review sheet, load `weekly-content-calendar.md` and `review-scorecard.md` first.

## Local Notes

- This skill is designed to be automation-friendly.
- Use it with automation prompts when the user wants recurring daily execution.
- For real browser publishing or troubleshooting, do not replace the platform skills; route through them.

## Reference Files

- Use [references/flywheel-operating-system.md](references/flywheel-operating-system.md) for the concrete 8 平台运营方案。
- Use [references/daily-automation-spec.md](references/daily-automation-spec.md) for the recurring-task breakdown and daily execution checklist.
- Use [scripts/validate_flywheel_skill.rb](scripts/validate_flywheel_skill.rb) to check that the skill keeps its required files and references.
