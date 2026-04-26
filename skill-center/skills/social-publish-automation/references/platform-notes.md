# Platform Notes

Read only the section for the current platform.

## 小云雀 / 剪映网页版源视频

- In this workspace, 小云雀 was workable as an upstream short-video generator, not as a one-click final-publish system.
- The stable packaging order was:
- lock one core judgment first
- generate one master vertical MP4
- keep subtitle lines mobile-readable
- export one platform package with title, description, and covers before opening creator backends
- For founder-IP talking-head videos, do not send the asset downstream until four checks pass:
- the person still reads as the intended founder
- the scene matches the message
- the subtitle line length stays easy to scan
- the planned cover route is clear per platform
- When the task requires short mobile subtitles, keep each spoken subtitle line within about 8 Chinese characters.
- Treat a generated people video with weak identity, missing headroom, or bad framing as a source-asset failure. Regenerate it first instead of trying to hide the issue with cover edits alone.

## Weibo

- Login was enough for this flow.
- Verify success from the public post URL, not only from the composer UI.

## 百家号

- Final publish can be blocked by `百度安全验证` even when the form already passes validation.
- Treat the slider or captcha as a manual checkpoint.
- After the user clears it, retry publish immediately and confirm from `作品管理`.

## 今日头条 / 头条号

- Use the creator backend entry `主页 -> 创作 -> 图文` for PC article publishing.
- Mobile article entry can also be useful for user instructions: `今日头条 APP -> 首页右上角发布按钮 -> 写文章` or `我的 -> 创作中心 -> 发布 -> 写文章`.
- Prefer an already-valid creator session before touching the editor.
- Desktop login may require SMS code, password login, or authorized 抖音 login.
- If the current device and browser have not passed SMS verification in the last 30 days, login or publish-time verification can be triggered.
- Use realistic editor input for title and body; do not rely on raw DOM assignment.
- If monetization is desired and available, the publish settings can enable `投放广告赚收益`.
- Only mark `头条首发` when the article is truly original, has more than 100 Chinese characters, and will not be posted elsewhere within 72 hours.
- Verify from `作品管理`, visible success text, or a public article URL.
- In the verified local blocker, missing creator login state left the flow on the verification-code login page, and switching to password login did not reliably expose the password form.
- Treat that state as a manual login checkpoint first, not as an editor bug.

## 微信公众号

- The editor can detect browser plugins and show `当前使用的浏览器插件存在安全隐患`.
- Final send can also be blocked by:
- `运营规则学习提醒`
- temporary group-send throttling
- `系统繁忙`
- Practical split:
- automation fills title, body, media, and metadata
- human handles quizzes, rate limits, and final send when the account is restricted

## 微信视频号

- As of the user-provided 2026-04-23 operating rule in this workspace, the standard initial publish URL is `https://channels.weixin.qq.com/platform/post/create`.
- Use `platform/post/list` as a management and verification surface, not as the default first page for a new publish run.
- The real publish form lives inside the `micro/content/post/create` frame, not the outer shell page.
- A visible logged-in home page at `https://channels.weixin.qq.com/platform` does not guarantee that `platform/post/create` is still usable.
- In the verified 2026-04-05 blocker, the home dashboard stayed logged in while direct navigation to `https://channels.weixin.qq.com/platform/post/create` redirected to `login.html`.
- Treat that state as a real relogin checkpoint for the publish route, not as a frame-selector bug.
- If Playwright frame locators are flaky, use the frame's default CDP execution context instead of an isolated world.
- For local video upload, the stable large-file path is `DOM.setFileInputFiles` with the frame-side input `objectId`.
- 2026-04-26 verified front-Chrome fallback: when Browser Bridge/OpenCLI cannot access the real editor but the logged-in Chrome publish page is visible, copy the real video and standalone cover to short non-symlink `/tmp` paths, use the native chooser `Cmd+Shift+G` to select those exact paths, and verify each accepted upload before continuing.
- In that fallback, never use a symlink such as `/tmp/vhvideo.mp4`; use a real copied file such as `/tmp/vhvideo-real.mp4`. The cover should likewise be a real copied standalone PNG such as `/tmp/vhcover-standard.png`.
- After upload, wait until the page no longer shows transient upload state such as `请上传视频`, `取消上传`, or `0%` before editing cover or publishing.
- On 视频号, after custom-cover editing the page can still show `文件上传中，请等待完成后再发表。` while the description and short title already look filled.
- Treat that as an upload-in-progress state, not as a field failure. Wait until the upload text disappears and the `发表` button loses `weui-desktop-btn_disabled`, then publish.
- The working field map in this workspace was:
- description editor: `.input-editor`
- short title: `input[placeholder="概括视频主要内容，字数建议6-16个字符"]`
- cover entry: `.edit-btn.edit-btn-zIndex`
- cover frame picker: `.key-frames-slider`
- cover confirm: `确定`
- In this workspace's 视频号 flow, `视频描述` and `短标题` are required fields and should be re-read before publish.
- Do not rely only on setting `.textContent` or `.value`; use real typing or a framework-aware setter, then verify the resulting description text and short-title value.
- A verified 2026-04-05 repair proved that real keyboard typing was the reliable path; DOM-visible values alone were not enough.
- In the 2026-04-04 video号 UI, after upload the cover block can expose a smaller overlay text `编辑` inside `封面预览 / 个人主页和分享卡片(3:4)`.
- Prefer clicking that visible `编辑` node first, then fall back to `编辑封面` or `.edit-btn.edit-btn-zIndex`.
- In the verified custom-cover path, opening `编辑封面` exposed two file inputs in the frame; the second file input accepted `image/jpeg,image/jpg,image/png`, and the required standard in this workspace is to upload a prepared local cover there rather than accepting the default frame cover.
- For the same cover modal, clicking the outer `确认` wrapper was not reliable in this workspace. The stable close/apply action was the inner primary button (`.weui-desktop-btn.weui-desktop-btn_primary...`).
- A successful publish can keep the top URL on `/platform/post/create` while the page itself shows visible `已发表`.
- Permission failures are still real platform states: if a visible dialog says `你还不能发表视频`, stop and treat it as an operator-role problem.
- On 视频号, multiple open `channels.weixin.qq.com/platform/post/create` tabs can exist at the same time with the same URL but different draft state.
- If only a shell or list tab is currently open, reuse that tab and navigate it to `https://channels.weixin.qq.com/platform/post/create` before starting the publish flow.
- If a create tab and a list tab are both open, reactivate the create tab before each upload, field write, cover edit, and final submit. The list tab can steal focus after native file selection.
- Before retrying a publish, scan the open create tabs and the `视频管理` list, otherwise the automation can target the wrong draft and create duplicate publishes.
- On 视频号, duplicate publishing is now treated as a hard failure condition. If the same video already exists in `视频管理`, stop and do not retry publish from another draft.
- If a create tab already contains an uploaded video but the current `视频描述` and `短标题` do not both match the target content package, treat that tab as an unsafe old draft and do not reuse it.
- If the custom-cover upload route is unstable, a practical fallback is to reopen `编辑`, choose a frontal keyframe from `img.key-frames`, wait for the page to show `封面已更新`, and only then continue to publish.
- If the user deletes a previous 视频号 post and asks for a clean republish, do not trust the previous draft state after refresh.
- Re-read the live form and make sure all three are visibly present again before publish:
- uploaded video
- `视频描述`
- `短标题`
- After a 视频号 republish, use the list page as the final truth source. A valid success is the new row itself carrying the expected right-side description snippet, not only a create-page `已发表` state.
- Do not count 视频号 as success until the second verification passes:
- pre-publish exact readback of `短标题` and `视频描述`
- confirmed cover-applied state after cover handling
- post-publish list-row verification against the standard content package
- A stricter 2026-04-22 update now applies:
- do not trust create-page visible text alone for 视频号
- if the page is Vue-managed and the final published row can diverge from DOM-visible text, verify the framework-managed state or payload before submit
- after submit, read the newest management-row component data directly when possible
- for 视频号, exact newest-row `shortTitle` and exact newest-row `description` are stronger than partial list snippets
- cover verification should use the newest-row thumbnail as the final proof, not only the compose-page preview
- 2026-04-26 verified Shadow DOM field path: find the shadow root that contains `.input-editor`, write `视频描述` into `.input-editor`, write `短标题` into `input[placeholder="概括视频主要内容，字数建议6-16个字符"]`, dispatch input/change events or use real typing, then read both exact values back from the same shadow root before pressing `发表`.
- In the same successful run, scroll the shadow `.app-body` to the bottom and click the real visible `发表` button only after all pre-submit checks pass. The final proof was the list count increasing and the newest row showing the expected date, description snippet, and standalone cover thumbnail.
- For founder-IP videos, the 3:4 cover should prefer a frontal keyframe or custom cover that clearly shows the person's face, hairline, and upper body, not only the background scene.

## 知乎

- Rich-text validation is sensitive to real edit gestures.
- If `发布` stays disabled, type into the body with realistic input.
- If needed, manually type one character and delete it to force editor activation.
- Recheck bridge connectivity before resuming a half-finished article.
- For 小云雀 founder-topic article packages in this workspace, when the current 知乎 flow does not expose a standalone cover upload, use the prepared local cover as the default 题图 / 首图 asset instead of leaving the opening visual uncontrolled.

## 小红书

- Creator publish may redirect to login if the creator session is missing.
- API moderation and UI availability are separate states.
- A publish request can still be rejected with `-9136` for community-rule issues.
- Real note creation hits `edith.xiaohongshu.com/web_api/sns/v2/note`.
- In CDP-attached remote Playwright, `setInputFiles` can fail over 50 MB with `Cannot transfer files larger than 50Mb...`.
- The stable workaround is to set the local file through CDP `DOM.setFileInputFiles` against the page-side file input.
- After submit, `笔记管理` may lag. Recheck list state before classifying the attempt as failed.
- The verified manager path for duplicate checks in this workspace is `https://creator.xiaohongshu.com/new/note-manager?source=official`.
- Use the real publish button node, not wrapper text or container divs.
- `修改封面` is not reliably clickable as plain visible text in the resting page state.
- The stable path in this workspace was:
- upload video
- wait for the edit form
- trigger the hidden hover operator inside the cover block
- wait for the actual modal signal `上传图片`
- upload the prepared cover image through the modal-side image input
- confirm, then publish
- In the verified local path, the best success signal was `success: true` plus `share_link`, then `笔记管理` showing the new note in `审核中`.
- The 2026-04-23 duplicate-publish incident showed that `笔记管理` lag by itself is not enough to justify a retry.
- The hard-stop duplicate guard is:
- local receipt at `automation/python-platform-takeover/state/publish-receipts/<campaign_id>.json`
- then `笔记管理`
- then public note visibility if available
- if any side confirms `submitted / published / under_review / success / verified`, do not republish the same campaign/platform.
- Only clear the receipt or force replacement after the old item has been deleted, made private, or explicitly abandoned.

## 抖音

- Cross-platform rule added on 2026-04-06 for 小云雀 founder content: after the source video is generated, immediately prepare one local `3:4` vertical cover and one local `4:3` horizontal cover, each carrying an 8 to 10 Chinese-character theme. Use those prepared covers on 抖音、快手、B站、视频号、微博, and use the same local cover package as the default article-cover source for 百家号、今日头条 / 头条号、知乎, unless the user explicitly overrides the rule.

- Upload and submit were straightforward after login in this workflow.
- `审核中` should be treated as successfully submitted.
- If the user chooses Douyin's own AI cover path, do not assume one modal confirm is enough.
- Verified local sequence:
- open `设置封面`
- pick the horizontal AI cover first
- click `设置竖封面`
- pick the vertical AI cover
- return and click `完成`
- The title field `填写作品标题，为作品获得更多流量` is a real required field separate from the description editor.
- A filled description plus a visible red `发布` button is not sufficient; re-read the title input value before submitting.
- In the 2026-04-05 retry, the title field was not stable with direct `input.value = ...` assignment. The reliable path was a real click into the field plus keyboard typing, then re-read the live value before publish.
- After publish, confirm from `作品管理` and inspect the top thumbnail card, because the composer can remain on the same URL even when submission fails or remains incomplete.
- Default founder-video rule in this workspace changed on 2026-04-05: use `上传封面` with a prepared local cover for both `竖封面3:4` and `横封面4:3`; do not use Douyin `AI封面` unless the user explicitly overrides that rule again.
- In founder-IP use cases, keep iterating AI cover candidates until the vertical cover shows the person clearly enough. A cover that mostly shows office background or crops away the body should be treated as a failed cover pick, not as acceptable output.
- In the verified 2026-04-05 Day 3 flow, custom upload covers worked only after explicitly clicking `保存` inside the cover modal after each image upload.
- A more reliable 2026-04-05 custom-cover path was verified after that: in the `设置封面` modal, click the black `上传封面` tile itself and write the file into the tile-owned input `.upload-BvM5FF input.semi-upload-hidden-input-replace`.
- Success should not be inferred from the click alone. Re-read the modal preview and the outer form: a real success switches the preview to the text cover and changes the form block from `选择封面` to visible `竖封面3:4 / 横封面4:3`, often with `封面检测中`.
- Do not verify a fresh Day 3 Douyin publish only by the short title field. The manage card can surface the long description text as the visible title while the actual submission is already live.
- Before retrying Douyin after a partial failure, re-open `作品管理` and check the top two rows by timestamp and description, otherwise automation can create duplicate same-day posts.

## 百家号

- Do not verify new longform from the home dashboard card alone.
- The reliable verification page is `https://baijiahao.baidu.com/builder/rc/content`.
- In the verified Day 1 longform flow, publish success first appeared as `提交成功，正在审核中...`, then the new article showed in `作品管理 / 内容管理`.
- Cover upload should target the image file input `input[type="file"][accept="image/*"]`.
- For 小云雀 founder-topic article packages in this workspace, the prepared local cover should be the default cover-upload source; do not leave 百家号 on AI封图 by default.
- Duplicate same-title retries can create a false “违规” outcome on the second copy while the first copy remains valid.
- Before retrying 百家号, open `作品管理` and check the exact title first.
- Treat delete as incomplete until the confirm dialog is accepted and the row disappears after refresh.

## 头条号

- The cover panel exposes two image file inputs; the first image input is the one that reliably reaches `已上传 1 张图片`.
- For 小云雀 founder-topic article packages in this workspace, the prepared local cover should be the default upload source instead of a generic automatic cover.
- After `预览并发布`, the final submit button is `确认发布`, not a generic `发布`.
- For longer article bodies in this workspace, DOM paragraph injection was more stable than large keyboard text insertion.
- Confirm final state from `作品管理`, where `审核中` is a successful submission.

## 快手

- Draft resume is a valid path when the initial upload lands in an editable draft.
- For larger local videos, CDP `DOM.setFileInputFiles` against the page-side input was more stable than ordinary remote `setInputFiles`.
- The verified description editor node was `#work-description-edit`.
- The verified submit target was the bottom action area containing `发布 / 取消`, not wrapper text elsewhere on the page.
- Confirm result from `作品管理`.
- `审核中` is the expected post-submit state.
- If the current page shows `还有上次未发布的视频，是否继续编辑？`, prefer resuming that draft before opening a new upload.
- In the verified 2026-04-04 flow, 快手 exposed both custom cover upload and `智能推荐封面`.
- Default founder-video rule in this workspace changed on 2026-04-05: switch to `上传新封面 / 上传封面 / 更换封面` and write the prepared local cover into the image input; do not use `智能推荐封面` unless the user explicitly overrides that rule again.
- For 小云雀 founder videos in this workspace, the prepared cover set should be built immediately after video generation, and the uploaded local cover remains the default publish path.
- Before retrying 快手 after an interrupted multi-platform run, re-check `作品管理` by exact duration and description. In the verified 2026-04-05 next-video flow, the latest `00:34` item was already `已发布 2026-04-05 15:57`; re-running at that point would only create a duplicate.

## B站

- Login may require SMS verification before reaching投稿.
- In this workspace, B站 upload can surface a short-message verification modal during or right after video upload.
- If the modal falls into a stale state such as `验证码过期，请重试`, do not keep hammering `获取验证码` in place.
- Stable recovery path:
- click the modal's top-right close button first
- wait for the verification modal to auto-appear again
- then click `获取验证码` one more time from the fresh modal
- only after that should the run pause for the user's SMS code
- Default founder-video rule in this workspace changed on 2026-04-05: upload a prepared local cover before final submit instead of leaving the default frame.
- For 小云雀 founder videos in this workspace, the same prepared cover set should include a B站-ready horizontal cover carrying the same 8 to 10 Chinese-character theme.
- `创作声明` is hidden under `更多设置`.
- The declaration UI is a custom dropdown; text-only clicks often miss the real interactive node.
- The first `.select-controller` is usually the `分区` selector, not the declaration selector.
- The declaration selector is the second `.select-controller`.
- Reliable sequence:
- expand `更多设置`
- target the declaration control inside `声明与权益`
- for AI-generated founder videos in this workspace, use `作者声明：该视频使用人工智能合成技术`
- if the declaration options do not render as visible DOM items, directly set the ancestor Vue form field `neutral_mark` to the exact declaration string
- type title and description through real editor input
- click the bottom submit control rather than the visible text alone
- In the verified flow, the effective submit node was `.submit-add`.
- Success is confirmed by the page state `稿件投递成功`.
- `定时发布` must be enabled through the real page switch first; only then does the time picker become valid.
- If B站 raises `定时发布时间不可用，请重新选择`, do not keep retrying submit. Confirm the dialog, reopen the timer, and move to the earliest valid slot that is at least 5 minutes ahead.
- In the verified 2026-04-06 flow, a requested `11:00` publish had already drifted too close; the correct recovery was to move the live draft to `11:10`, verify both `.date-picker-timer` and `.time-container`, and only then click `.submit-add`.
