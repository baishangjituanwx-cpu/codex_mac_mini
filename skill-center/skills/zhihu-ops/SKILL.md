---
name: zhihu-ops
description: Operate a 知乎 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to choose the right Zhihu format, post or repair an answer/article/idea workflow, review 创作中心 and收益 signals, handle comments or moderation decisions, research current community rules, or improve material for trust and distribution.
---

# Zhihu Ops

## Overview

Use this skill for 知乎日常运营. It is tuned for the platform's trust-heavy content style: strong structure, clear sourcing, disciplined interaction, and careful rule boundaries.

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Start by choosing the right form:
- `回答` for demand already expressed as a question
- `文章` for structured argument or longer narrative
- `想法` for lightweight update or fast reaction
- `视频` when visual explanation materially helps
- Before writing, confirm the target question, angle, evidence base, and whether the author has enough domain legitimacy for the claim being made.
- For browser-side publish flows, use realistic editor input and verification through `$social-publish-automation`.

### 2. Data Analysis

- Review performance through `创作中心`, and where available `收益分析`.
- Official creator materials indicate that content quality, interaction data, reading volume, vertical consistency, and posting frequency all matter for creator incentives and reach.
- Do not read numbers in isolation. Review:
- reading and interaction together
- whether the content stayed in one clear vertical
- whether the format matched the topic
- whether comments show trust, confusion, or skepticism
- Use low-comment, high-read posts differently from high-comment, polarized posts.

### 3. Comment Interaction

- Handle comments with a serious, professional, friendly tone.
- Reply early to clarification requests, evidence challenges, and thoughtful disagreement.
- Use moderation features for clear abuse, spam, or garbage information rather than engaging every low-signal provocation.
- If a comment thread degrades the discussion quality, treat folding, reporting, or non-engagement as an operational choice, not a failure to interact.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before posting borderline material.
- The main rule themes visible in official creator guidance are:
- no title bait
- no hard-selling or diversion
- no plagiarism or stitched aggregation
- no unrelated images or low-information packaging
- no fake identity, fake credentials, or data tampering
- Content should stay grounded in reliable information and domain fit.

### 5. Material Optimization Suggestions

- Optimize for trust before virality.
- Improve weak material in this order:
- sharpen the question or thesis
- add stronger sourcing or firsthand detail
- clean up structure and subheads
- reduce empty rhetoric and unsupported conclusions
- use images only when they add understanding
- The platform's own creator guidance emphasizes trusted sources, clear structure, careful language, and images as support rather than decoration.

## Local Notes

- In this workspace, the biggest 知乎 publishing issue was editor activation: plain DOM injection did not count as real edited content, leaving publish disabled.
- A real typing gesture, sometimes as small as adding and deleting one character, can unlock the editor state.
- In this workspace's founder-IP workflow, once 小云雀 has generated the upstream content package, 知乎 should default to the prepared local cover as the article's 题图 or首图 when the current flow does not expose a separate cover-upload field.
- Keep login, recovery, and verification details out of notes and generated artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for the official creator-manual links, incentive signals, and community-rule summaries used by this skill.
