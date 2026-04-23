---
name: xiaohongshu-ops
description: Operate a 小红书 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to publish or troubleshoot a note, review note-manager state and message feedback, handle comments, check current rule boundaries, or improve covers, captions, and note packaging for better distribution and compliance.
---

# Xiaohongshu Ops

## Overview

Use this skill for 小红书日常运营. It covers note publishing, postmortem review, comment handling, rule lookup, and packaging advice.

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Build the package first: cover, title, note body, tags, media assets, and intended CTA.
- For browser-side publishing or troubleshooting, route through `$social-publish-automation`.
- Do not trust page access alone. On 小红书, UI availability and moderation outcome are separate states.
- Before any retry, check both `笔记管理` and the local publish receipt for this campaign. If either already shows the same note in a blocking state, stop and do not publish again.
- Verify from `笔记管理`, the returned publish response, or the public note URL when available.
- `笔记管理` lag is a recheck problem, not a republish signal.
- If this run already returned `success: true` or `share_link`, record the local publish receipt immediately and treat the note as already submitted until disproven.
- A re-publish is allowed only after the old item has a real structural defect and has already been deleted, turned private, or explicitly abandoned.

### 2. Data Analysis

- Review from creator-side note-management and message surfaces where available.
- Track at least:
- whether the note actually entered the manager list
- likes, saves, shares, and comments
- comment quality and repeated questions
- whether the packaging matches the note's real topic
- Use lag-aware judgment. A request can succeed while manager visibility lags.

### 3. Comment Interaction

- Reply early to genuine usage questions, product-selection questions, and trust-building comments.
- Avoid arguing with obvious bait or traffic-farming comments.
- Save recurring objections and uncertainty points as input for the next note, pinned comment, or revised cover.
- Treat comments as conversion and topic-research signals, not only engagement numbers.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before publishing promotional or borderline content.
- Priority risks:
- community-rule rejection after submit
- login/session loss
- weak note-cover relevance
- hard selling or external-platform diversion
- wrapper-node clicks that miss the real publish control
- If the platform returns a rule-style rejection, fix the package first instead of repeatedly resubmitting the same note.

### 5. Material Optimization Suggestions

- Improve weak material in this order:
- sharper cover promise
- clearer first-screen value
- tighter title and note-topic alignment
- more concrete product or scenario detail
- cleaner CTA that feels native to note discussion
- Optimize for save-worthiness and trust, not just curiosity clicks.

## Local Notes

- In this workspace, the stable 小红书 blockers were:
- creator publish can redirect to login when session is missing
- publish API can return `-9136` for community-rule rejection
- note creation can succeed while `笔记管理` still lags
- the real publish target is the true button node, not a wrapper div
- in CDP-attached remote Playwright, normal `setInputFiles` can fail above 50 MB; the stable workaround was page-side CDP `DOM.setFileInputFiles`
- the strongest success signal was `success: true` plus `share_link`, then `笔记管理` showing the new note in `审核中`
- the hard-stop duplicate guard is `笔记管理` plus the local publish receipt ledger under `automation/python-platform-takeover/state/publish-receipts/`
- Keep credentials, verification codes, and private account details out of notes and artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official source links and local publishing lessons.
