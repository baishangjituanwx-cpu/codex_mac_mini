---
name: platform-cover-ops
description: Fix and optimize cover workflows across 微博、百家号、知乎、今日头条 / 头条号、抖音、小红书、微信视频号、快手. Use when Codex needs to improve article covers, note covers, video thumbnails, first-frame packaging, AI-generated cover revisions, crop-safe exports, or browser-side cover troubleshooting after upload.
---

# Platform Cover Ops

## Overview

Use this skill when the main problem is not the正文 or脚本 itself, but the封面、题图、首帧、缩略图、分享卡片 preview, or the platform-specific cover-edit flow after upload.

This skill decides whether the target platform wants:

- no separate cover object, so the first image or first frame is the real cover
- a default auto or AI cover that must be revised manually
- a frame picker after upload
- an uploaded custom static cover
- a hybrid preview that shows both feed and share-card crops

If the task also requires real browser actions, use this skill together with `$social-publish-automation`.

## Core Workflow

### 1. Classify the cover surface first

- `无独立封面字段`:
- optimize the first image, first frame, and first visible line together
- typical for 微博图文 and many 知乎文章 workflows
- `默认首帧 / 默认自动封面`:
- do not accept the default blindly
- re-pick the frame or upload a custom cover
- typical for 视频号、快手、小红书视频
- `AI 生成封面 / 自动推荐封面`:
- treat the AI result as a draft, not the final answer
- manual second edit is expected
- typical for 抖音 and some 百家号 / 头条 cover helpers
- `强审核封面`:
- cover mismatch, low-quality text posters, and noisy marketing graphics can directly hurt distribution or审核
- typical for 百家号、头条号

### 2. Build a reusable cover package before touching the UI

- Prepare four variants when time matters:
- `master-3x4`: a vertical poster with one main subject and one short promise
- `safe-frame`: a no-text clean frame that still works if the platform strips or crops text
- `square-1x1`: for small-card or share-card preview checks
- `landscape-16x9`: for platforms that still surface wide thumbnails in some lists
- For 小云雀-generated founder content in this workspace, the default package is stricter:
- generate the video first
- immediately build one `vertical-3x4` cover and one `horizontal-4x3` cover
- put one 8 to 10 Chinese-character theme on both covers
- use those prepared covers on 抖音、快手、B站、视频号、微博
- and use the same local cover package as the default article-cover source for 百家号、今日头条 / 头条号、知乎
- For 大陈 / AI员工 Seedance content packages, this cover package must permanently follow the migration-pack style in `smb://BSJT168._smb._tcp.local/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428`:
- use `project/scripts/generate_simple_video_covers.py` when mounted, or an exact visual equivalent if unavailable
- output `cover-vertical-3x4.png` and `cover-horizontal-4x3.png`
- use a lower-middle rounded dark translucent information card, gold/white dimensional main title, and one subtitle line
- do not substitute a plain full-width bottom band, platform auto cover, AI recommended cover, or unstyled frame
- every downstream platform publish package must explicitly point to these prepared cover files
- Keep text short:
- one conflict or one promise
- usually 6 to 14 Chinese characters
- do not repeat the entire title on the cover
- Keep the subject large and central:
- assume the outer 10 to 15 percent may be cropped or visually ignored
- do not put key text at the extreme top or bottom

### 3. Route to the platform-specific cover logic

- Read [references/platform-notes.md](references/platform-notes.md) and load only the current platform section.
- Use this quick routing rule:
- 微博 / 知乎:
- first image or first frame is usually more important than chasing a nonexistent separate cover field
- 百家号 / 头条号:
- article cover quality and title-cover match are high priority
- 抖音:
- review the post-upload AI or default cover and revise it manually
- 小红书:
- cover is the real click surface; treat it like a note card, not a raw video still
- 微信视频号:
- always inspect both personal-homepage and share-card preview
- 快手:
- manual key-frame selection or custom cover is usually better than accepting the default frame

### 4. Verify the cover at thumbnail size

- Do not trust only the full-size editor preview.
- Verify at list-card size:
- can the main subject still be recognized?
- is the text still readable?
- does the title and cover tell the same story?
- if the cover becomes unreadable at roughly 25 percent scale, redo it
- For video-platform covers in this workspace, `cover exists` is not a pass condition. The cover must pass a 25 percent scale readability check before submit:
- render or export a small preview, for example about `300x400` for a `3:4` cover
- main cover title must be readable without opening the original image
- the main人物/主体 must remain clearly visible at list-card size; a dark poster with readable text but hidden人物 is a cover failure
- key text must not be covered by人物、原视频字幕、进度条、平台角标, or crop edges
- if readability is uncertain, stop and rebuild the cover rather than publishing
- After publishing or cover repair, verify the management-list thumbnail, not only the upload/editor preview.
- If an already-published item has a wrong or unreadable cover, repair that existing item first. Do not republish the same content unless the old item has been deleted, hidden, or explicitly marked obsolete by the user.
- The receipt note must distinguish `cover_thumbnail_present` from `cover_readability_passed`; only the latter can close a cover-sensitive platform task.
- Browser-side cover upload must use a real file upload mechanism, not page-side JavaScript assignment to `input.files`. Prefer Playwright `set_input_files`, OpenCLI `setFileInput`, or CDP `DOM.setFileInputFiles` against an image-only file input such as `input[type="file"][accept*="image"]`.
- Do not use AppleScript to type long local paths into the macOS file chooser for cover upload. If a system file picker is unavoidable, treat it as a manual checkpoint or choose the file through a visible folder, not through automated path typing.
- On Windows, if a system file picker is unavoidable, use an exact short real path such as `%TEMP%\\cover-upload.png` or a quoted `C:/.../cover-upload.png` in the chooser's file-name box. Do not rely on Explorer search results, `.lnk` shortcuts, OneDrive placeholders, or symlink targets for cover upload.

## Platform Map

### 微博

- Treat `首图 / 视频封面 + 前 18 到 24 字` as one combined click unit.
- If the post is 图文, the first image effectively acts as the cover.
- If the post is 视频, optimize the video cover but still rewrite the first line with the cover in mind.

### 百家号

- Cover is a strong审核 and分发 variable, not decoration.
- If AI cover generation fails or produces invalid previews, switch to manual local upload immediately.
- Keep the cover tightly aligned with a search-style question title.
- For 小云雀 founder-topic article packages in this workspace, default to uploading the prepared local cover instead of relying on AI封图.

### 知乎

- Use cover or首图 as a trust signal, not an ad poster.
- Prefer evidence-style visuals, screenshots, charts, or scene proof over decorative marketing art.
- If there is no strong dedicated cover field in the current flow, optimize the opening image and article first screen instead.
- For 小云雀 founder-topic article packages in this workspace, use the prepared local cover as the default 题图 or首图 asset when a dedicated cover upload is absent.

### 今日头条 / 头条号

- If an article gets impressions but zero reads, treat the cover and title as the first repair target.
- Avoid abstract brand posters; use a clear business problem or process-change scene.
- Never let the image and title drift apart, because image-text mismatch is a real credit risk.
- For 小云雀 founder-topic article packages in this workspace, default to uploading the prepared local cover rather than accepting a generic auto result.
- For Seedance video content packages in this workspace, 头条号 must prefer the generated vertical `3:4` cover as the platform-specific primary cover; keep the horizontal `4:3` cover only as a fallback unless the user explicitly requests otherwise.
- On a Windows repo mirror, keep that same priority in the handoff files: the upload matrix and content-package fields should point at the real quoted vertical `3:4` cover path first, with the horizontal `4:3` cover listed only as fallback.

### 抖音

- The post-upload default or AI-generated cover is only a first pass.
- Manual second edit is the normal workflow, not a special case.
- Align the cover with the first 1 to 3 seconds so users do not feel a bait-and-switch.

### 小红书

- Cover is the note's true packaging front, especially in list view.
- A usable 小红书 cover should look like a native note, not a generic brand poster.
- If the current publish flow does not expose a satisfying cover editor, prepend a clean poster frame at the head of the video.

### 微信视频号

- Do not leave the default first frame if it contains motion blur, subtitles, or weak composition.
- The current verified flow supports:
- selecting a frame from video
- uploading a custom cover
- checking homepage and share-card preview
- For 小云雀 founder videos in this workspace, default to the uploaded custom cover path rather than frame-only cover selection.
- Before final submit or repair submit, the uploaded cover must be checked as a small list-card thumbnail; if the cover title cannot be read there, or the founder人物 is hidden by a dark overlay, replace the cover before clicking `发表` or `确认修改`.
- After `修改描述和封面`, a `修改审核中` row means the repair was submitted, not fully verified. Keep the item in pending repair state until the management-list thumbnail updates and passes readability.
- If a failed repair leaves the row showing `作者修改过视频信息` and the edit action is disabled, stop trying to force hidden cover-edit routes. The remaining safe choices are waiting for the platform to reopen editing, or replacing the item only after the old item is deleted/hidden/approved obsolete.

### 快手

- The platform supports custom cover in desktop upload flows.
- If the current route only exposes a frame picker, choose a clear action frame with large subject focus.
- If the route exposes custom cover upload, prefer a prepared cover when the raw video frame is weak.
- For 小云雀 founder videos in this workspace, prefer the prepared uploaded cover as the default, not `智能推荐封面`.

## Local Notes

- In this workspace, the strongest verified cover-edit path is 微信视频号:
- cover entry `.edit-btn.edit-btn-zIndex`
- frame picker `.key-frames-slider`
- confirm `确定`
- current UI also exposes `从视频中选择封面` and `上传封面`
- 百家号 had a verified blocker where AI cover previews rendered as error or undefined and the confirm button stayed disabled; manual upload resolved it.
- 快手 officially supports custom covers in desktop upload, but the current verified local publish flow focused on video upload plus description, so cover customization should be checked per route before assuming the control exists.
- 小红书 and快手 both benefit from a pre-baked first frame when browser-side cover controls are weak or inconsistent.
- This skill now includes two Ruby helpers:
- `scripts/validate_cover_skill.rb` for checking the skill's own structure
- `scripts/preflight_cover_briefs.rb <briefs.json>` for checking real cover-brief batches for missing fields, overlong copy, and weak safe-zone definitions

## When to Combine With Other Skills

- For actual publishing, draft resume, or browser-side cover editing:
- also use `$social-publish-automation`
- For broader platform operations beyond cover work:
- pair this skill with the matching platform ops skill
- `$weibo-ops`
- `$baijiahao-ops`
- `$zhihu-ops`
- `$toutiao-ops`
- `$douyin-ops`
- `$xiaohongshu-ops`
- `$wechat-channels-ops`
- `$kuaishou-ops`

## Reference File

- Use [references/platform-notes.md](references/platform-notes.md) for official links, platform-specific cover mechanics, and local verified cover-edit notes.
- Use [references/cover-playbook.md](references/cover-playbook.md) for the ready-to-run 8 平台实战版: cover rewrite, suggested cover copy, crop-safe zones, and execution order.
- Use [references/cover-template-matrix.md](references/cover-template-matrix.md) for the second-layer template system: 4 content archetypes adapted across all 8 platforms.
- Use [references/cover-prompt-kit.md](references/cover-prompt-kit.md) when you need AI-image prompts, layout prompts, or designer-ready cover briefs instead of only strategy guidance.
