---
name: social-publish-automation
description: Browser-driven content publishing and troubleshooting through OpenCLI / Browser Bridge or CDP-attached Chrome for Chinese creator platforms. Use when Codex needs to publish, resume drafts, verify posting status, or debug blocked submissions on Zhihu, Weibo, WeChat Official Accounts, WeChat Channels, Baijiahao, 今日头条 / 头条号, Xiaohongshu, Douyin, Kuaishou, or Bilibili.
---

# Social Publish Automation

## Overview

Use this skill to execute or repair browser-based publishing flows on Chinese content platforms.
Prefer it when the task involves:

- posting existing text, image, or video assets
- resuming a half-finished draft after login or verification
- diagnosing why a submit button, editor, or publish API does not complete
- verifying whether a submission is published, submitted, under review, or still unconfirmed

## Core Workflow

1. Confirm bridge health.
- Run `opencli doctor`.
- Stop if `Extension: not connected`.
- If Browser Bridge is down but the dedicated logged-in Chrome is healthy on a known CDP port, CDP-attached Playwright is an acceptable fallback.
- Prefer that fallback for logged-in creator backends when restarting the browser would risk losing session state.

2. Isolate the browser session.
- Use a unique OpenCLI `workspace` per platform flow.
- Avoid reusing a workspace across unrelated platforms or retries.

3. Prepare the publish package before touching the UI.
- Confirm local asset paths, title, body, declarations, and platform-specific extras.
- Avoid mid-flow content rewriting unless the platform rejects the original package.
- Before any retry or补发, check the target platform's management list for the exact same title or asset first. If an item already exists in a terminal or near-terminal state such as `已发布`, `审核中`, or `审核未通过`, stop and resolve that item instead of auto-reposting.

4. Prefer real interactive nodes over visible text.
- Use snapshot refs or stable selectors instead of naive DOM text clicks.
- Expect custom dropdowns, hidden sections, and wrapper elements.
- Re-open hidden sections such as `更多设置` before assuming a required field is missing.

5. Use realistic input for editors.
- Prefer bridge typing for titles, descriptions, and rich-text editors when plain DOM assignment does not activate validation.
- Re-read page state after typing instead of trusting the write call.
- For remote CDP sessions, large local videos may fail through normal `setInputFiles` transfer. In that case, set files through CDP with a page- or frame-side input handle and a local filesystem path.

6. Treat risk controls as manual checkpoints.
- Pause for SMS codes, sliders, safety challenges, rule quizzes, and forced scans.
- Resume from the current page after the user clears the checkpoint instead of restarting the entire flow.

7. Verify outcomes outside the click itself.
- Confirm with visible status text, management pages, creator lists, public URLs, or intercepted responses.
- Distinguish `已发布`, `已提交`, `审核中`, and `请求已发出但未入库`.

## Operating Rules

- Keep credentials out of notes, screenshots, and generated artifacts.
- Assume plugin-detection warnings reduce automation reliability.
- Capture exact blocking text before changing strategy.
- If a platform-specific section exists for the target site, read the matching section in [platform-notes.md](references/platform-notes.md) first.
- For 今日头条 / 头条号图文发布, also check the platform section for entry path, login gates, and verification expectations before automating the editor.
- If the browser stays on the compose URL after submit, do not assume failure. Some platforms surface a reliable in-page terminal state such as `已发表` without redirecting.

## Feishu Notify Rule

- After each platform reaches a verified publish-success state, immediately send one Feishu message for that platform before moving on to the next platform.
- The fixed notify chat on this machine is `oc_45f4f2c2f0a783f636969cd821179f40`.
- Do not wait until the whole batch finishes. The push should happen per platform.
- Do not send on button click alone. Only send after one of these verified states is confirmed:
- `已发布`
- `提交成功`
- `已提交`
- `审核中` with confirmed list-entry or success-page landing
- Use a separate message per platform. Do not merge multiple platforms into one message unless the user explicitly asks.
- Default send toolchain:
- prefer `./node_modules/@larksuite/cli/bin/lark-cli` from `/Users/baishangjituan/Documents/New project`
- fallback to global `lark-cli` if the local binary is unavailable
- Preferred send form:
- `lark-cli im +messages-send --as bot --chat-id "oc_45f4f2c2f0a783f636969cd821179f40" --text "<message>"`
- Minimum message fields:
- platform
- title or asset identifier
- verified state
- verification time
- publish URL or management URL when available
- If the exact same platform and same item were already pushed in the current run, do not send a duplicate unless the user explicitly asks for a re-test or re-send.

## Verification Pattern

After a publish attempt, record:

- current URL
- visible success or failure text
- management-list presence
- public URL if available
- API response if interceptable

If the click succeeds but the status is ambiguous, treat the result as unconfirmed until one of those signals resolves it.

Once the result is confirmed and notify-worthy, send the Feishu push immediately, then continue to the next platform.
