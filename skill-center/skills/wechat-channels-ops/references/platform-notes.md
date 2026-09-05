# WeChat Channels Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 视频号助手能力与入口

Source:
- https://training.tencentads.com/uploads/202108/qScnaaFK_t6LQKJ.pdf

Observed on:
- 2026-04-02

Key points:
- The official Tencent training PDF says `视频号助手` login URL is `https://channels.weixin.qq.com/login`.
- It states 视频号助手 supports:
- publishing HD video
- scheduled publishing
- binding operators for collaborative management
- a live-data dashboard for all and single-session live statistics
- The same PDF also uses `channels.weixin.qq.com` as the desktop management surface for live and content operations.

### 视频号助手真实入口

Sources:
- https://channels.weixin.qq.com/login.html
- https://channels.weixin.qq.com/platform/post/create
- https://channels.weixin.qq.com/micro/content/post/list

Observed on:
- 2026-04-02

Key points:
- These are the actual official login, publish, and content-list surfaces seen in local operation.

## Operating Guidance

- Check operator role first. Many apparent publish bugs are actually permission problems.
- When reviewing content, separate public-feed distribution from private-domain spread and follow-up conversation.
- For live-adjacent assets, review data in three buckets: exposure, interaction, and conversion.

## Local Practice Notes

- Current workspace lessons:
- a fresh WeChat scan may be required before the assistant can continue
- the actual publish form lives inside `iframe[name="content"]`
- without admin or operator permission, the platform can block publish with `你还不能发表视频`
- a verified successful publish landed in the list page at `https://channels.weixin.qq.com/micro/content/post/list` with visible `已发表`
- when normal Playwright frame locators were unreliable, the stable path was the frame's default CDP execution context
- large local videos uploaded reliably through `DOM.setFileInputFiles` with the frame-side file-input `objectId`
- the compose form should not be treated as ready while it still shows `请上传视频`, `取消上传`, or `0%`
- even after description, short title, and cover are visible, `发表` can remain visually disabled while the frame still says `文件上传中，请等待完成后再发表。`
- in that state, do not retry upload or re-edit immediately; wait for the upload text to disappear and for the `发表` button to lose the disabled style, then publish
- verified field map:
- description editor `.input-editor`
- short title input `input[placeholder="概括视频主要内容，字数建议6-16个字符"]`
- cover edit trigger `.edit-btn.edit-btn-zIndex`
- frame chooser `.key-frames-slider`
- confirm button `确定`
- `视频描述` and `短标题` should be treated as mandatory for this workspace's video号 publishing standard.
- Do not trust raw DOM assignment alone for those two fields. Use real typing or a framework-aware setter, then read the values back before publish.
- In the 2026-04-04 republish incident, leaving either `视频描述` or `短标题` blank after a refresh led to an incomplete publish standard even though the video and cover were already present.
- For any retry after delete or refresh, re-read both fields from the live form and refill them before pressing `发表`.
- on 2026-04-04, the current publish UI also exposed the cover trigger as the overlay text `编辑` inside the `封面预览 / 个人主页和分享卡片(3:4)` card
- safe order now is: upload video -> wait for `封面预览` -> try the visible `编辑` overlay first -> fall back to `编辑封面` or `.edit-btn.edit-btn-zIndex`
- in the verified custom-cover path on 2026-04-03, `编辑封面` opened a modal that already contained two file inputs; the second one accepted `image/jpeg,image/jpg,image/png`
- that meant the stable route was: open `编辑封面` -> write the local cover file into the second file input -> click `确定` -> click `发表`
- the create page can remain open after submit; visible `已发表` on that page is still a valid success signal
- on 2026-04-04, a fresh publish with `xyq-ai-founder-video-2026-04-04.mp4` and a custom 3:4 cover succeeded and the list page showed a new item at `2026年04月04日 16:28`
- on 2026-04-04, repeated retries left multiple `channels.weixin.qq.com/platform/post/create` tabs open with the same URL but different draft states
- before acting on 视频号, scan all open `post/create` tabs and choose the one whose frame text matches the intended draft, otherwise retries can target the wrong draft and create duplicate publishes
- before any republish, open `视频管理` first and check whether the same video row or the same description snippet is already present; if it is, stop and do not publish a duplicate
- when the custom-cover upload path is unstable, a stable fallback is:
- reopen `编辑`
- select a frontal keyframe from `img.key-frames`
- confirm the 3:4 cover update until the page itself shows `封面已更新`
- only then continue to publish
- For founder-IP videos, treat `大陈正面清晰可见` as the real cover requirement in the 3:4 preview, not just “there is a cover.”
- on the same day, that fallback path created duplicate publishes at `2026年04月04日 17:24` and `2026年04月04日 17:27`, so list-page dedupe checks should happen before any retry
- on 2026-04-05 next-video publish, a fully empty `platform/post/create` form was enough to complete the whole flow directly: upload video -> wait for `封面预览 / 短标题` -> fill `视频描述` and `短标题` -> open `编辑` -> upload local 3:4 cover through the second file input -> `确定` -> `发表`
- from 2026-04-06 onward, the stricter default is: `编辑封面` must end with a real local cover upload; do not accept the default frame-only cover as a valid publish result
- on the same run, raw frame text still contained hidden legacy dialog strings such as `你还不能发表视频` and `管理员本人验证`, but the visible page was a clean publish form and the publish succeeded. For 视频号, visible UI state is more trustworthy than aggregated `innerText` when hidden dialogs linger in DOM.
- another verified 2026-04-05 repair path worked from a half-finished ready page after the user deleted a bad publish:
- keep the existing uploaded video, description, and short title
- click the visible `编辑` overlay inside `封面预览 / 个人主页和分享卡片(3:4)`
- the `编辑封面` dialog exposes `上传封面` plus a crop confirm flow
- the real custom-cover input remains the second `input[type="file"]`
- after writing the local cover, click `裁剪封面图 / 确定`
- the success toast `已发表` can appear while the cover dialog is still visibly open; treat that toast plus list-page presence as a valid success
- on 2026-04-05 late-night republish, standard Playwright frame locators were unreliable in the remote CDP session even though the upload input existed in DOM:
- `locator('input[type="file"]').first().setInputFiles(...)` could hang on attach
- an `ElementHandle` derived from `evaluateHandle(document.querySelector(...))` could already be detached by the time `setInputFiles(...)` ran
- the stable path remained CDP `DOM.setFileInputFiles` against the frame-default execution context `objectId`
- if the page already shows uploaded video, filled description, and filled short title, resume from that state instead of re-uploading the video again
- in that resumed state, upload the custom cover through the second `input[type="file"]`, click the visible `确定`, then publish
- verified successful republish result:
- short title `先配AI员工`
- list page new item at `2026年04月05日 19:48`
- If the task expands into browser execution, also load `$social-publish-automation`.

- add a final visual verification step for 视频号 republish: after `已发表`, inspect the saved create-page screenshot to confirm the uploaded cover actually shows the intended title text before closing the task.
- verified 2026-04-05 acceptable packaging set: cover main `先配AI员工`, cover subline `再谈扩团队`, short title `再谈如何扩团队`, list entry time `2026年04月05日 19:55`.

- 2026-04-05 diagnosis: visible description and short-title text inside the create form is not sufficient proof for 视频号. In this workspace, direct DOM mutation (`textContent`, `value`, plus synthetic input/change) can render correctly in the page while the published item still lands without title metadata.
- The issue persisted across both tested orders (`upload -> fill fields` and `fill fields -> upload`), so sequencing alone is not the root cause.
- Treat 视频号 description and short title as framework-bound fields: use real typing or a native setter path that updates component state, then verify via a stronger signal than DOM text alone.
- A later verified 2026-04-05 fix used real keyboard typing for both fields before publish, then validated from the list page that the right-side text snippet actually contained the full description.
- For the cover modal, clicking the outer `确认` wrapper did not close the dialog reliably. The stable target was the inner primary button element (`.weui-desktop-btn.weui-desktop-btn_primary.weui-desktop-btn_mini`).
- The toast `封面已更新` was transient and disappeared from `innerText` quickly. Do not require it as a lasting DOM string before publish; use the saved screenshot plus the list-page result as the stronger final proof.
- The local 3:4 PNG `/Users/z/Downloads/Codex/outputs/dachen-next-video-frames-2026-04-05/frame-30s-wechat-3x4-retitle.png` was accepted after this fix path and the list page showed a new row at `2026年04月05日 21:07` with the expected description snippet.
- 2026-04-06 operating rule: for 视频号, `same video do not republish` is now a hard stop. If the list page already contains the same video, handle cleanup or edit instead of running another publish.
