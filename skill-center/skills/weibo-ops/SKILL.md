---
name: weibo-ops
description: Operate a 微博 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to draft or post a Weibo update, analyze creator-center metrics, manage comments or 协管员 workflows, check current 微博 credit and community rules, or improve copy and assets for reach and compliance.
---

# Weibo Ops

## Overview

Use this skill for 微博日常运营 work. It covers five recurring jobs on the same platform:

- publish or resume a post
- review performance data
- handle comments and interaction workflows
- research current platform rules
- improve copy, images, and topic framing

If the task requires real browser operation, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Prepare the package first: copy, images or video, topic tags, links, and the intended call to action.
- For browser-side publishing or troubleshooting, route the execution through `$social-publish-automation`.
- If a post fails to send, check the official failure causes first: account restriction, unsafe links, rule violations, risky account state, or client/network issues.
- Do not brute-force retries. Capture the exact blocking text and fix the content or account issue first.

### 2. Data Analysis

- Use `创作者中心` and `数据中心/数据助手` as the primary review surface.
- Official caveats matter:
- data center and data assistant can disagree because of deduping and deleted-post handling
- the current center mainly shows yesterday, 7-day, and 30-day windows rather than live intraday data
- accounts below 1 万粉 may not see full data details
- Review at least:
- reading or play growth
- 转评赞
- public versus private traffic
- new followers and 铁粉 changes
- per-post收益 if the account uses creator monetization
- Compare strong and weak posts by opening pattern, visual relevance, and comment quality rather than by raw views alone.

### 3. Comment Interaction

- Check comments, mentions, private messages, and public feedback loops after posting.
- Reply fast to useful questions, factual corrections, and purchase-intent or conversion-intent comments.
- Remove obvious abuse, spam, or rumor amplification, but do not over-clean normal disagreement.
- If the account needs scale moderation, use the official `协管员` feature on mobile. It supports comment management, but actions are not reversible, so use trusted helpers only.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before making assumptions about rule boundaries.
- Priority rule areas on 微博:
- credit-history penalties
- unsafe links
- personal attacks and cyberbullying
- rumor or false information
- low-quality or samey monetized content
- If monetization is enabled, remember that low-quality, samey, or违规 content can reduce or cancel revenue, not just reach.

### 5. Material Optimization Suggestions

- Use data and rule signals together. A post with poor reach may be weak, or it may be under-distributed for compliance reasons.
- Improve weak posts in this order:
- tighten the first sentence
- increase image-text relevance
- remove vague or risky links
- make the user value clearer
- raise comment-worthy specificity instead of adding empty emotion
- When optimizing for monetized posts, prioritize originality, useful detail, higher interaction quality, and a stable posting cadence over slogan-heavy copy.

## Local Notes

- In this workspace, 微博发布本身没有出现明显平台级阻断，登录后流程相对直接。
- In this workspace's founder-IP workflow, 微博 should default to `文案 + 1 张问题型首图`; a text-only version should be treated as incomplete unless the user explicitly wants pure text.
- In this workspace's founder-IP video workflow, once 小云雀 has generated the video, the default next step is to build a vertical and a horizontal prepared cover with one 8 to 10 Chinese-character theme, and use that prepared poster in the 微博 video package instead of leaving the raw default frame.
- Verification should still happen from the public post URL or profile feed, not only from the composer result.
- Keep credentials, SMS codes, and recovery details out of notes and generated artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official source links, data caveats, interaction tooling, and credit-risk notes.
