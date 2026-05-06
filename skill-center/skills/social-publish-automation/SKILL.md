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

1. Confirm Chrome DevTools / CDP access first.
- For actual publishing tasks, first try to attach to the already logged-in Chrome through Chrome DevTools Protocol / CDP.
- Check known local CDP endpoints such as `http://127.0.0.1:9222/json/version` or the active `BROWSER_CDP_URL` before choosing an automation route.
- On a Windows repo mirror, verify that endpoint with `Invoke-WebRequest http://127.0.0.1:9222/json/version` first. Only use `automation/python-platform-takeover/scripts/start-chrome-cdp.ps1` when a new CDP-capable browser session is truly needed; do not relaunch an already logged-in browser just to normalize the tooling path.
- If CDP is available, prefer CDP-attached Playwright, Chrome DevTools Protocol calls, or the existing Python/CDP takeover scripts for DOM inspection, file inputs, submit clicks, network/API verification, and management-list proof.
- Do not restart the user's logged-in Chrome just to enable CDP unless the user explicitly approves it; preserving creator-platform login state is more important than a cleaner automation surface.
- If CDP is unavailable, run `opencli doctor` and use OpenCLI / Browser Bridge against the current logged-in Chrome tab.
- On the Windows repo mirror, `automation/python-platform-takeover/scripts/social-publisher.ps1 doctor --check-browser --package <yaml> --platform <platform>` is the first fallback check before deciding whether Browser Bridge is safe enough.
- Stop if neither CDP nor Browser Bridge can safely reach the real editor or management page.

2. Isolate the browser session.
- Use a unique OpenCLI `workspace` per platform flow.
- Avoid reusing a workspace across unrelated platforms or retries.

3. Prepare the publish package before touching the UI.
- Resolve and lock the active `campaign_id` before opening any platform editor:
- Prefer the newest local `content-package.*.yaml` whose matching content-library package is `status: ready_for_publish`, unless the user explicitly names an older campaign.
- Compare the locked `campaign_id`, video path, cover paths, and platform title/description against the intended task. If they do not match, stop before upload.
- If the newest ready package has no matching receipt file under `state/publish-receipts/`, create or initialize that receipt for the new campaign. Never fall back to the previous campaign's receipt just because it is the latest existing receipt.
- If an older receipt is `published` but a newer ready package exists, treat the older receipt as historical only; it must not satisfy or block the newer campaign's publishing task.
- On Windows in this repo, keep that lock check on the shared CLI path: `.\scripts\social-publisher.ps1 validate-package <yaml>` plus `receipt-status` / `record-receipt --status not_started` against the same `campaign_id`, not a separate handwritten checklist.
- If the package declares handoff-only publish constraints such as `publish_constraints.allow_live: false`, `no_publish_in_handoff_generation: true`, `no_upload_in_handoff_generation: true`, or `no_submit_click_in_handoff_generation: true`, stop at validation and receipt initialization. On Windows, record the package state with `.\scripts\social-publisher.ps1 receipt-status <yaml>` or `record-receipt --status not_published`, but do not run `publish --execute`, do not open the native chooser, and do not click submit.
- If a Hermes handoff package includes `fingerprints` and `lock_dir`, preserve those values on Windows exactly as received. They are part of the duplicate-prevention contract, not optional metadata to rewrite or drop during package cleanup.
- On Windows, treat `automation/python-platform-takeover/state/hermes-handoff/latest.json` as valid only when it still points to a real `ready_for_publish` campaign. If it points to a smoke-test package, `/tmp` scratch package, or stale historical package, stop and repair the handoff instead of publishing from it.
- Confirm local asset paths, title, body, declarations, and platform-specific extras.
- Avoid mid-flow content rewriting unless the platform rejects the original package.
- For video platforms with a custom cover, run a cover-readability preflight before opening the platform editor: view or render the cover at roughly 25 percent scale and confirm the main title is readable in the small preview.
- If the cover depends on text, a thumbnail URL or uploaded-file state is not sufficient. The package is incomplete until the cover title is visually readable in a list-card-sized preview.
- For browser-side cover uploads, never use page-side JavaScript to assign `input.files`; that can bypass the platform upload service. Use Playwright `set_input_files`, OpenCLI `setFileInput`, or CDP `DOM.setFileInputFiles` on an image-only file input.
- Do not type long local paths, Finder search strings, or symlink paths into a macOS native file chooser through AppleScript as a normal automation fallback. On Windows, do not rely on Explorer search results, `.lnk` shortcuts, or symlink targets as the upload path either. If direct file injection fails, stop unless the platform has a verified short-path fallback.
- Verified macOS short-path fallback rule: copy the real asset to a short non-symlink `/tmp/<simple-name>` path, select it with the native chooser `Cmd+Shift+G`, and immediately verify the platform UI accepted the upload. If the UI does not visibly accept the upload, stop instead of continuing.
- Verified Windows short-path fallback rule: copy the real asset to a short non-symlink `%TEMP%\\<simple-name>` path such as `$env:TEMP\\vhvideo-real.mp4`, paste that exact path into the chooser's file-name box, confirm `Open`, and immediately verify the platform UI accepted the upload. Do not use a shortcut or symlink for this fallback.
- Before any retry or补发, check the local publish receipt ledger first. The hard-stop ledger for this workspace lives under `automation/python-platform-takeover/state/publish-receipts/<campaign_id>.json`.
- Before any retry or补发, check the target platform's management list for the exact same title or asset first. If an item already exists in a terminal or near-terminal state such as `已发布`, `审核中`, or `审核未通过`, stop and resolve that item instead of auto-reposting.
- Default rule: do not re-publish the same platform item just because this round's UI flow looked unstable.
- A same-platform re-publish is allowed only when all of the following are true:
- the published item has a real structural defect, such as wrong正文、错误标题、错误封面、错误视频、关键字段缺失
- the old item has already been manually deleted,转仅自己可见, or explicitly marked by the user as obsolete
- the local publish receipt has been cleared, or the operator is explicitly forcing replacement after verifying the old item is gone
- the replacement package has been re-checked against the intended content library entry before re-submit
- If the problem is only weak performance, slow review, or uncertain button behavior, do not re-publish. Verify first.

4. Prefer real interactive nodes over visible text.
- Use snapshot refs or stable selectors instead of naive DOM text clicks.
- Expect custom dropdowns, hidden sections, and wrapper elements.
- Re-open hidden sections such as `更多设置` before assuming a required field is missing.

5. Use realistic input for editors.
- Prefer bridge typing for titles, descriptions, and rich-text editors when plain DOM assignment does not activate validation.
- Re-read page state after typing instead of trusting the write call.
- If the platform is Vue- or React-driven and the visible editor still diverges from the eventual published result, escalate to a framework-aware setter path and verify the platform's own payload or store state before submit.
- For remote CDP sessions, large local videos may fail through normal `setInputFiles` transfer. In that case, set files through CDP with a page- or frame-side input handle and a local filesystem path.

6. Treat risk controls as manual checkpoints.
- Pause for SMS codes, sliders, safety challenges, rule quizzes, and forced scans.
- Resume from the current page after the user clears the checkpoint instead of restarting the entire flow.

7. Verify outcomes outside the click itself.
- Confirm with visible status text, management pages, creator lists, public URLs, or intercepted responses.
- Distinguish `已发布`, `已提交`, `审核中`, and `请求已发出但未入库`.
- When the platform exposes framework-managed row data or API payloads, prefer those exact fields over partial visible snippets.
- For 微信视频号 publishing in this workspace, use `https://channels.weixin.qq.com/platform/post/create` as the standard direct-entry URL. Treat the list page as a verification surface, not the default initial publish surface.
- For 微信视频号, if Browser Bridge / OpenCLI cannot reach the real editor but the logged-in Chrome page is visible and healthy, use the verified front-Chrome fallback: target the existing create tab, upload video and cover from short real temp paths through the native chooser (`/tmp` plus `Cmd+Shift+G` on macOS, `%TEMP%` plus exact-path file-name entry on Windows), write Shadow DOM fields, verify exact values, then submit and verify the newest management row.

## Operating Rules

- Keep credentials out of notes, screenshots, and generated artifacts.
- Assume plugin-detection warnings reduce automation reliability.
- Capture exact blocking text before changing strategy.
- If a platform-specific section exists for the target site, read the matching section in [platform-notes.md](references/platform-notes.md) first.
- For 今日头条 / 头条号图文发布, also check the platform section for entry path, login gates, and verification expectations before automating the editor.
- If the browser stays on the compose URL after submit, do not assume failure. Some platforms surface a reliable in-page terminal state such as `已发表` without redirecting.
- For 微信视频号, do not accept create-page `已发表` or DOM-visible editor text as sufficient proof by themselves. Require exact post-publish verification from the newest management-row data, including title, description, and expected cover thumbnail.
- For cover-sensitive platforms, especially 微信视频号、小红书、头条号, `expected cover thumbnail` must mean visually readable at management-list size and the main人物/主体 must remain recognizable. If it is only present but unreadable, or the text is readable while the人物 is hidden by a dark overlay, treat the publish as structurally defective and repair the existing item instead of republishing.
- If a platform marks an item as already modified and disables the edit action, stop the repair loop. Do not force hidden edit URLs; treat the item as locked until editing reopens or the old item is intentionally replaced.

## Feishu Notify Rule

- After each platform reaches a verified publish-success state, immediately send one Feishu message for that platform before moving on to the next platform.
- The fixed notify chat on this machine is `oc_45f4f2c2f0a783f636969cd821179f40`.
- Do not wait until the whole batch finishes. The push should happen per platform.
- Do not send on button click alone. Only send after one of these verified states is confirmed:
- `已发布`
- `提交成功`
- `已提交`
- `审核中` with confirmed list-entry or success-page landing
- For 微信视频号, `处理中` with a confirmed newest management-row object ID, exact title/description, and readable intended cover thumbnail is also notify-worthy.
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

## Anti-Duplicate Guard

- For each platform in the current batch, always run this decision order before any retry:
- `先锁定本轮 campaign_id / 内容包版本`
- `先查本地发布台账`
- `先查管理页`
- `再查公开页 / 主页 / 作品流`
- `最后才决定是否允许重发`
- The local receipt check is valid only when the receipt `campaign_id` exactly matches the locked content package. A previous-day or previous-campaign receipt is evidence for that old campaign only.
- If the platform management page shows a recent row whose title/body belongs to a different campaign than the locked package, do not count it as success for the current task and do not use it as a reason to publish another copy of the old campaign.
- Treat local receipt statuses `submitted / published / under_review / success / verified` as blocking states by default.
- Treat `blocked_account_review_pending` as a blocking state too. It means the platform is stopping publish because the account or creator profile is still under review; do not clear the receipt or retry publish until that review resolves or the user explicitly changes the plan.
- Do not hand-edit `state/publish-receipts/<campaign_id>.json` just because it now carries extra verification keys such as `verified_fields`, `aid`, or `object_nonce`. In this workspace the shared CLI and receipt loader are expected to tolerate unknown metadata; use `receipt-status`, `record-receipt`, or `clear-receipt` instead of deleting fields by hand.
- If the management list or public profile already shows a same-day item with the same core title, same video, or same正文片段, treat it as an existing publish candidate, not as a failed attempt.
- For 微信视频号, the anti-duplicate guard is stricter than exact-match blocking:
- if any recent management-row item reuses the same `短标题` and the platform-side `description` is still highly similar to the current package, stop before publish
- do not rely on “different date” or “slightly changed wording” as proof that it is a new item
- when this near-duplicate condition is hit, the operator must first change the title or the body skeleton, not just replace a few nouns
- When an existing item is found, the default action is:
- `不重发`
- `先修正旧条` or `先确认旧条状态`
- Only after the user has made the old item unavailable or clearly approved replacement should a new publish be attempted.
- For 小红书 specifically, `success: true`, `share_link`, or a blocking local receipt means the note has crossed the success threshold. `笔记管理` lag is not a reason to repeat-publish.
- If a manual browser path succeeds before the manager list catches up, immediately record the local receipt. Do not rely on memory alone.

For 微信视频号 in this workspace, the minimum verified-success standard is:

- pre-publish exact editor readback of `短标题` and `视频描述`
- if needed, framework-level payload or store check that those values will really be submitted
- pre-publish recent-content duplicate check against the newest management rows; same `短标题` plus highly similar `description` is a hard stop
- post-publish newest-row exact match on platform-side `shortTitle`
- post-publish newest-row exact match on platform-side `description`
- newest-row thumbnail consistent with the intended uploaded cover
- newest-row thumbnail title readable at list-card size and founder人物/主体 visible, or row state explicitly shows `修改审核中` after a submitted cover repair
- submit-click validation that the real `button` was clicked; if only a wrapper `DIV` was clicked and no list state changes, treat the submit as not executed
- if list and create tabs coexist, reselect the create tab before every upload, field write, and submit; list-tab focus jumps are a known source of false input and stale verification

Once the result is confirmed and notify-worthy, send the Feishu push immediately, then continue to the next platform.
