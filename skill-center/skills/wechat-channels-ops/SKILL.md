---
name: wechat-channels-ops
description: Operate a 微信视频号 account across publishing, data review, comment interaction, rule research, and material optimization. Use when Codex needs to publish or troubleshoot via 视频号助手, review live or post data, handle comment interaction, check operator-permission and originality settings, or improve titles, covers, and private-domain-friendly content packaging.
---

# WeChat Channels Ops

## Overview

Use this skill for 微信视频号日常运营. It covers 视频号助手发布、复盘、互动、规则和素材优化。

If the task requires real browser execution, also use `$social-publish-automation`.

## Workflow

### 1. Publish

- Build the package first: video file, short title, description, cover, category, and any private-domain distribution plan.
- For browser-side execution, route through `$social-publish-automation`.
- Use `视频号助手` as the main desktop operation surface.
- For video publishing in this workspace, treat `https://channels.weixin.qq.com/platform/post/create` as the standard direct-entry URL.
- If a correct `platform/post/create` tab is already open, take over that tab directly.
- If only a 视频号助手 shell or list tab is open, reuse that existing tab and navigate it to `https://channels.weixin.qq.com/platform/post/create` before starting the publish flow.
- If both `platform/post/create` and `platform/post/list` tabs are open, explicitly target the create tab before every upload, field write, and submit action. The list tab can steal focus after file selection; never type or click based on the last active tab without rechecking the URL.
- If multiple create tabs exist, use only the tab whose live draft matches the intended package. Do not reuse an old draft with a different video, description, short title, or cover.
- Treat `视频描述` and `短标题` as required packaging fields for video posts, not optional extras.
- For this workspace, descriptions and short titles are framework-bound fields. Do not trust plain DOM assignment alone.
- Prefer real typing first. If the visible editor text and platform payload diverge, use a framework-aware setter path that updates the page's own component state, then verify the payload again before publish.
- If the publish form is exposed through Shadow DOM, the verified field targets are the shadow-root `.input-editor` for `视频描述` and `input[placeholder="概括视频主要内容，字数建议6-16个字符"]` for `短标题`. Use native setters / input events or real typing, then read back both exact values from the same shadow root before submit.
- For 小云雀 founder videos in this workspace, generate the video first, then immediately build the prepared cover set: one vertical `3:4` cover and one horizontal `4:3` cover, each with one 8 to 10 Chinese-character theme.
- Before clicking `发表`, read both fields back from the editor and stop if either one did not persist.
- For 视频号 specifically, editor readback is necessary but not sufficient. The stronger pre-publish check is that the page's framework-managed publish payload also contains the exact target `短标题` and `视频描述`.
- When submitting, click the actual visible `button` whose normalized text is `发表`. Do not click a surrounding `DIV` / `.weui-desktop-btn_wrp` wrapper unless it contains no real button and a follow-up state check proves the click submitted. Wrapper clicks can be no-ops.
- For custom cover upload, do not stop at opening the modal or seeing the uploaded preview. Always upload a prepared local cover inside `编辑封面`, confirm the modal through the inner primary action button, and then verify the compose page has accepted that uploaded cover.
- Do not use page-side JavaScript to fake `input.files` for 视频号 cover upload. It can make the UI look changed without calling the platform's real upload service. Use one of the real file-injection paths only:
- Playwright `locator.set_input_files(<local_cover_path>)`
- OpenCLI `page.setFileInput([<local_cover_path>], 'input[type="file"][accept*="image"]')`
- CDP `DOM.setFileInputFiles` on the frame-side image file input
- The image selector must target `accept*="image"`; never use a generic `input[type=file]` if a video file input is also present.
- Native macOS file chooser path typing is not the default 视频号 upload path. Long paths, Finder search strings, and symlinks have produced malformed selections in this environment.
- If direct file injection cannot reach the input but the visible Chrome publish page is healthy, a controlled fallback is allowed: copy the asset to a short real `/tmp/<simple-name>` path, use `Cmd+Shift+G` to select that exact path, and immediately verify the UI accepted the upload. Never use a symlink for this fallback.
- Cover acceptance requires visual readability, not just a non-empty thumbnail URL. Before clicking `发表`, check the cover at a small management-list-like size and confirm the main cover title is readable and the founder人物/主体 is clearly visible. If the title is readable but the人物 is hidden by a dark overlay, treat it as a cover failure.
- If the published cover is wrong or unreadable, use the existing row's `修改描述和封面` repair flow. Do not republish the same video only to fix a cover.
- After `修改描述和封面`, click the outer `完成`, then the final `确认修改`; if the row shows `修改审核中，预计30分钟内审核完成`, record the state as `cover_repair_under_review` and verify again after review before marking the cover fully fixed.
- If the newest row later shows `作者修改过视频信息` and the row's `修改描述和封面` action has class `disabled`, the post-publish repair path is closed. At that point, do not keep retrying hidden routes; the only safe options are waiting for the platform to reopen editing, or replacing the item after the old item is deleted/hidden/explicitly marked obsolete.
- Before any retry or republish, check `视频管理` first. If the same video is already present in the list, stop instead of publishing a duplicate.
- Before any fresh publish, check the newest management rows for recent near-duplicates.
- If a recent row already uses the same `短标题` and the platform-side `description` is still highly similar to the current package, stop before publish. That is a content-repeat incident, not a new post.
- Verify that the current WeChat account has the correct operator role before spending time inside the editor.
- Confirm final state from the content list or visible `已发表` signal, not only from the submit button.
- For retries, the strongest final proof is the management list's newest row carrying the expected title and description in the platform-side row data, not only create-page text or a partial visible snippet.
- Use `视频管理 / platform/post/list` for two purposes only:
- pre-publish duplicate checks
- post-publish second verification
- Do not mark success until the newest management-row payload shows:
- exact `shortTitle`
- exact `description`
- expected cover thumbnail on the newest row
- readable cover title in the newest-row thumbnail, or an explicit `cover_repair_under_review` state if a submitted cover repair is still pending platform review

### 2. Data Analysis

- Review from 视频号助手 and related data surfaces where available.
- Track at least:
- publish status and list presence
- comments and interaction quality
- replay or live data if the asset was used in a live workflow
- follow-up private-domain response such as shares, reminders, or friend-group spread when relevant
- For live or replay content, separate exposure, interaction, and conversion steps instead of using one total number.

### 3. Comment Interaction

- Reply fast to trust-building questions, product or scenario clarifications, and conversion-intent comments.
- Use comments to identify repeat objections and later private-domain follow-up angles.
- For live-style content, treat comment rhythm and interaction density as part of content quality.
- Do not over-engage trolls or obvious spam.

### 4. Rule Research

- Read [references/platform-notes.md](references/platform-notes.md) before publishing.
- Priority checks:
- current WeChat login state
- operator permission
- originality or分成 popups
- publish limits imposed by account role or tool access
- If the publish page is reachable but the account lacks permission, stop and fix role assignment instead of debugging selectors.

### 5. Material Optimization Suggestions

- Improve weak material in this order:
- clearer short title
- stronger first-screen promise
- better local or private-domain relevance
- tighter description with one clear action
- cleaner cover and category match
- For 微信生态 distribution, optimize for share-worthiness and follow-up conversation, not only feed impressions.

## Local Notes

- In this workspace, 视频号助手 has shown three stable realities:
- login may require fresh WeChat scan
- the real publish page content sits inside `iframe[name="content"]`
- operator permission matters; without admin or operator role the page can say `你还不能发表视频`
- As of 2026-04-23, the standard operational entry for publish is the direct create URL `https://channels.weixin.qq.com/platform/post/create`; the list page should not be used as the initial publish entry.
- A verified success path exists: after publish, the list page showed the new item and visible `已发表`.
- For large local videos, the stable upload path was CDP into the frame's default execution context plus `DOM.setFileInputFiles` on the frame-side file-input `objectId`.
- The compose form becomes truly ready only after temporary text such as `请上传视频`, `取消上传`, and `0%` disappears.
- The working field map in this workspace was:
- description editor `.input-editor`
- short title `input[placeholder="概括视频主要内容，字数建议6-16个字符"]`
- cover edit entry `.edit-btn.edit-btn-zIndex`
- cover frame chooser `.key-frames-slider`
- cover confirm path: open `编辑封面`, upload through the cover-upload input, then click the modal's inner primary confirm button
- A successful publish may keep the outer URL on `/platform/post/create`; if the page itself shows `已发表`, treat it as success.
- A later 2026-04-05 verified path proved three extra rules:
- `视频描述` and `短标题` need real keyboard input to persist into the final publish result
- the transient `封面已更新` toast is useful but not durable enough to be the only success check
- the final verification should include the list row itself showing the expected description snippet
- if `视频管理` already shows the same video, do not retry publish from a stale draft or a second `post/create` tab
- A later 2026-04-22 verified path tightened this further:
- visible create-page text alone is not enough; the page can render the right body text while the published row still lands with empty `description`
- for 视频号, publish success should be judged from the newest list-row component data, not only visible text
- the current robust standard is: pre-publish exact editor readback + framework-payload check, then post-publish newest-row exact `shortTitle` and exact `description` check
- the same 2026-04-22 run also confirmed the correct cover should be validated from the saved newest-row thumbnail, not only the compose-page preview
- a later 2026-04-23 failure confirmed one more hard rule: same `短标题` plus high正文相似度 across recent rows must stop the publish before submit, even if the calendar date changed
- A 2026-04-25 cover postmortem confirmed a harder cover rule: JS assignment to `input.files` did not upload the prepared PNG; the saved row used a video frame thumbnail instead. The correct method is real file injection against `input[type="file"][accept*="image"]`, followed by list-thumbnail visual verification. That verification must include both cover text readability and人物主体可见性. If the row says `作者修改过视频信息`, the edit action can become disabled after one failed repair.
- A later 2026-04-25 retry confirmed that long-path AppleScript entry in the macOS file chooser can mangle the path and fail to find the file. Do not use that long-path route for cover uploads; use direct file injection first, or the verified short `/tmp` real-file fallback below.
- A verified 2026-04-25 replacement publish confirmed the safe path after the old bad item was manually deleted: Browser Bridge real file injection for the video, real file injection for the image cover input, exact editor readback, click the real `button` `发表`, then verify the new management-row `objectId`, exact `shortTitle`, exact `description`, and uploaded cover key in the list thumbnail.
- A verified 2026-04-26 replacement publish confirmed a stable front-Chrome fallback when direct bridge control cannot access the real editor but the logged-in page is visible:
- close or ignore the extra list tab and explicitly reactivate the intended `platform/post/create` tab before each action
- copy the real video and real standalone cover to short non-symlink temp files such as `/tmp/vhvideo-real.mp4` and `/tmp/vhcover-standard.png`
- upload the video through the visible upload box plus native chooser `Cmd+Shift+G` short path, then wait for the video preview and `封面预览`
- open `编辑` under `封面预览`, upload the standalone cover with the same short-path chooser fallback, click the inner modal `确认`, and verify the compose preview changes to the intended text-cover style
- write `视频描述` and `短标题` through the Shadow DOM field map, then read both exact values back before final submit
- scroll the shadow `.app-body` to the bottom, click the real `发表` button only after final operator authorization, then verify the list row count increased and the newest row shows the expected date, description snippet, and standalone cover thumbnail
- Keep QR codes, login details, and private operator information out of notes and artifacts.

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official 视频号助手 references and local operator-permission notes.
