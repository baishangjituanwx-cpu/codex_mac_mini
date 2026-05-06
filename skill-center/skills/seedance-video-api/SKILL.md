---
name: seedance-video-api
description: Use when the user wants to create, inspect, extend, poll, or download Volcengine Ark Seedance 2.0 / 2.0 Fast video tasks through the direct API, including text-to-video, first-frame image-to-video, multimodal reference generation, 15-second extension chaining, payload preparation with the bundled CLI, and the mandatory post-generation multi-platform cover package plus publish-copy package workflow; requires a locally set `ARK_API_KEY` and must never store or request the full key in chat or tracked files.
---

# Seedance Video API

Direct Volcengine Ark Seedance 2.0 / 2.0 Fast workflows for Codex. Use the bundled CLI and payload templates for safe direct API work instead of re-building requests each time.

## When To Use

- The user wants direct API access to `Seedance 2.0` or `Seedance 2.0 Fast`
- The user wants to submit or poll Ark video-generation tasks
- The user wants payload templates for text-to-video, first-frame image-to-video, multimodal reference video, or extension
- The user wants a publish-ready video content package with per-platform titles and concrete copy after generation
- The user wants to build longer videos from chained `4-15s` Seedance segments
- The user wants to download `video_url` or `last_frame_url` from an existing task
- The user needs a fixed `3:4` + `4:3` cover package immediately after video generation for multi-platform publishing

## Authentication Rules

- Live calls require `ARK_API_KEY` to already be set locally in the environment.
- Never ask the user to paste the full API key into chat.
- Never write API keys into the skill files, payload JSON, git-tracked `.env` files, shell scripts, or commit messages.
- Prefer environment-based auth only. Do not recommend passing secrets on the command line unless the user explicitly insists.
- If the key is missing, tell the user to set `ARK_API_KEY` locally and confirm when ready.

Safe default for the current shell session:

```bash
export ARK_API_KEY='...'
```

Windows PowerShell equivalent:

```powershell
$env:ARK_API_KEY = '...'
```

## Core Workflow

1. Decide the task type: new generation, query, wait, download, or extend.
2. Start from a bundled template in `assets/examples/`.
3. Edit the payload in the working directory, not inside the skill folder.
4. Dry-run first to verify the normalized request body.
5. Submit the task with `scripts/seedance_cli.py`.
6. Poll until terminal status if the user needs a finished asset.
7. Download the video or last frame promptly because result URLs expire.
8. Treat the generated video as incomplete until the cover package is also prepared.
9. Extract one clean key frame from the final video and build the mandatory `3:4` and `4:3` PNG cover set.
10. Treat the content package as incomplete until the publish-copy package is also prepared with per-platform titles and concrete copy.

## Prompt Output Standard

When the user only wants a Seedance prompt package and does not need a live API run yet, still use this skill.

Prompt-only defaults for this workspace:

- default duration is `15s`
- default ratio is `9:16` unless the user explicitly asks for another aspect ratio
- default resolution is `720p`
- first classify the request into `文生视频` or `图生视频` with the decision table in [references/prompt-template.md](references/prompt-template.md)
- if the user provides a real-person source image, treat that as the default `图生视频` path
- when real-person material is used, add strict identity-preservation language to the prompt
- for the `智者大陈 / 百亿联盟陈永俊` founder-office line, default structure is `3秒钩子 -> 剧情反转 -> 情绪共鸣 -> AI员工分工落地`
- for the `大陈 / AI员工 / 机器人小马` Seedance API line, include the female supporting role by default unless the user explicitly excludes it; use `asset://asset-20260401123823-6d4x2` as an additional `reference_image`
- subtitles, when present, must be model-generated: single Chinese line at a time, white text, transparent background, no black subtitle strip
- reserve the last `0.5-1s` for one clean, stable cover-ready frame in the video prompt
- output one video prompt plus one aligned cover-copy pair

Review-to-creative translation is mandatory:

- use the latest data-review result as strategy evidence, not as raw script text
- before writing the Seedance prompt, translate the review into a clear viewer-facing creative angle, conflict, scene action, and role motivation
- do not paste review phrases, platform status wording, dashboard task wording, file names, or internal复盘结论 directly into video dialogue or subtitles unless the phrase is intentionally simplified for audience comprehension
- turn operational findings into human scenes, for example `内容级指标缺失` should become a concrete office conflict such as `运营同事追问：播放、完播、互动在哪里`
- turn review recommendations into simple actions, for example `同账号3-7条同形态对照` should become `先比三条同格式内容再决定怎么改`
- dialogue must sound like clear spoken Chinese from the characters, not like a report, checklist, dashboard note, or automation log
- the prompt must still preserve one focused content point; do not cram every review item into one 15-second video
- keep internal evidence in `latest-review.md` or `brief.json`; keep `video-prompt.txt` audience-facing, scene-based, and easy for the video model to execute

When the user asks for anything longer than `15s`, do not fake it as one task. Produce either:

- one `15s` single-task package
- or a multi-segment plan split into multiple Seedance tasks

In prompt-only mode, output in this order unless the user asks for another format:

1. `生成模式`
2. `时长`
3. `比例`
4. `分辨率`
5. `视频主提示词`
6. `封面主标题`
7. `封面副标题`
8. `可直接提交的 JSON payload`
9. when relevant, one short note about extension or stitching

Use [references/prompt-template.md](references/prompt-template.md) for the fixed Seedance prompt-package structure and the current `15s` default.

When real-person material is used, the prompt must explicitly require:

- preserve the original person's hairstyle, face shape, facial features, skin tone, glasses if present, body shape, clothing, and overall recognizability
- preserve the original person's proportions, silhouette, and age impression unless the user explicitly asks for a compliant change
- do not change identity
- do not swap face
- do not drift into another outfit, another body shape, another face shape, or another hair design
- do not replace the original person with a stylized or generic actor
- do not casually rewrite the original person's clothing details, accessories, or visual persona

When the female supporting role is used, the prompt and payload must also explicitly require:

- include `asset://asset-20260401123823-6d4x2` as a separate `reference_image` in the Seedance payload
- treat the female role as a stable supporting character, not a replaceable background extra
- preserve the female role's original hairstyle, face shape, facial features, skin tone, body shape, clothing, accessories, age impression, and overall recognizability
- do not swap her face, change her outfit, change her body shape, turn her into a generic actor, or let her merge with 大陈 or 机器人小马
- keep the female supporting role's screen time meaningful but secondary; she should support the conflict, proof, or execution scene without stealing the main cover priority from 大陈 / AI员工

When prompting for a new generation, also require the ending shot to leave one usable cover frame:

- last `0.5-1s` should be a clear, stable, unoccluded half-body or close-up frame
- avoid motion blur, awkward mouth shapes, closed eyes, or face occlusion in that final hold
- keep the frame natural enough to read as a real video pause, not a pasted poster

## Mandatory Subtitle Rule

For the current founder-IP line in this workspace, subtitles are not optional polish; they are part of the generation rule.

Hard rule:

- subtitles must be generated by the model inside the video itself
- one Chinese line at a time
- white text
- transparent background
- no black subtitle strip
- avoid more than about `8` Chinese characters per subtitle line when possible

Forbidden:

- no `无字幕母片 + 本地后期补字幕` release path
- no local subtitle-overlay repair for typos, multi-line subtitles, black strips, or乱码
- no large opaque `drawbox` subtitle cover as a publish workaround

If subtitle quality is wrong:

- tighten the prompt
- regenerate
- do not patch locally and still call the asset publish-ready

## Mandatory Cover Package

For this workspace, Seedance video generation does not end at `output.mp4`.

Always plan for a reusable cover package after the video is finished:

- `cover-vertical-3x4.png`
- `cover-horizontal-4x3.png`

Required export specs:

- Vertical: `1080x1440`
- Horizontal: `1440x1080`
- Format: `PNG`

Required source-frame rules:

- The cover image must come from the generated video, not from the original reference photo.
- Pick the clearest frame with a sharp face, natural eyes, and a non-awkward mouth shape.
- Keep the main subject in a real office environment.
- Prefer half-body or close-up framing.
- Leave the bottom `30%` visually safe for title treatment.

Required packaging rules:

- For 大陈 / AI员工 Seedance content packages, the canonical cover style is permanently the migration-pack style from `smb://BSJT168._smb._tcp.local/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428`.
- Use the migration-pack script `project/scripts/generate_simple_video_covers.py` when that SMB package is mounted, or an exact visual equivalent if the package is unavailable.
- Do not replace it with a custom full-width bottom strip, plain white-title band, generic poster template, or platform auto/AI cover.
- The layout must use a lower-middle rounded dark translucent information card, gold/white dimensional main title, one short subtitle line, clean office frame, and no extra sticker clutter.
- Cover title text must be added after generation by the cover script; do not rely on Chinese text generated inside the video frame as the cover title.
- Visual priority is `大陈真实脸 + AI员工大字标题 + 老板收益/动作承诺`.
- The same cover package must be referenced by every downstream platform publish package; do not create a separate platform structure that forgets or bypasses these covers.

Copy rules:

- Main title: `6-10` Chinese characters
- Subtitle: `4-8` Chinese characters
- Must highlight `AI员工`
- Write result, replacement, or boss-benefit language instead of generic feature copy

Use `references/cover-package.md` for the full standard.
Use `references/cover-execution.md` for the helper-script flow and example commands.

If the task is mainly about producing, revising, or validating the cover package itself, also use [$platform-cover-ops](/Users/baishangjituan/.codex/skills/platform-cover-ops/SKILL.md).

## Mandatory Publish Package

For this workspace, a generated video is not a finished `内容包` until the downstream publish-copy files also exist.

Minimum required deliverables for a publish-ready video campaign:

- one Seedance prompt package
- one structured production brief such as `brief.json`
- one saved prompt artifact such as `video-prompt.txt`
- one saved normalized request payload such as `seedance_payload.json`
- one final `mp4`
- one `3:4` + `4:3` cover package
- one video publish package with platform-specific titles and concrete copy
- one platform upload matrix such as `platform-upload-map.md`
- one publish plan artifact such as `publish-plan.md` or `publish-plan.json` when browser-side publishing is the next step
- one final verification artifact such as `final-verify.json` when browser-side publishing has completed
- one Hermes content-package YAML in `automation/python-platform-takeover/configs/content-package.<campaign_id>.yaml` when the package status is `ready_for_publish`
- one initial Hermes receipt in `automation/python-platform-takeover/state/publish-receipts/<campaign_id>.json` with `status: not_published` and empty `receipts: {}`
- one Hermes direct JSON package in `automation/python-platform-takeover/configs/hermes-package.<campaign_id>.json`
- one Hermes latest pointer in `automation/python-platform-takeover/state/hermes-handoff/latest.json`

If browser-side publishing will follow immediately, also add:

- one browser-side execution checklist such as `browser-use-checklist.md`

The video publish package must contain real, paste-ready copy, not placeholders or title direction only.

Minimum required video-platform fields:

- 抖音：`标题` + `文案`
- 快手：`标题` + `文案`
- 视频号：`短标题` + `描述`
- 微博视频：`标题` + `配文`

If the same campaign is intended for B站 or downstream article / note platforms, also add:

- B站：`标题` + `简介`
- 百家号 / 知乎：`标题` + `正文/描述`
- 头条号：Seedance 视频内容包默认按视频发布生成 `标题` + `描述` + `上传视频`；只有用户明确要求图文时，才单独生成头条图文稿
- 小红书：默认按视频笔记生成 `标题` + `描述` + `上传视频`；只有用户明确要求图文笔记时，才标记 `不上传视频`

Package rules:

- use one unified topic, but do not force one identical title across all platforms
- generate platform titles and concrete copy from the latest completed data-review result first, not from generic topic intuition
- treat the latest completed multi-platform review as the primary evidence source for topic angle, hook priority, wording priority, platform differences, and what to keep / cut / retest
- data-review output must be secondarily interpreted before it becomes prompt, dialogue, title, or copy; never treat review text as publish-ready creative text
- write a short `latest-review.md` or `brief.json` note that separates `review evidence` from `creative translation`, so a later publish thread can see why the topic was chosen without exposing internal review wording as the video script
- if no fresh completed review exists for the current line, say so explicitly in the package and fall back to the latest validated review rather than inventing “latest signals”
- keep the platform title aligned with the same problem the cover is selling
- prefer `问题句 > 动作句 > 角色句` unless current review evidence says otherwise
- 视频号 `短标题` must be generated together with `视频描述`
- if a file is marked `ready_for_publish`, empty title or copy sections are invalid
- if the upload asset differs from the raw generated video, keep both paths and label them explicitly, for example `raw_video` vs `publish_video`
- one generated master video may be reused across all video-platform publish tasks unless a platform-specific upload asset is explicitly required
- every platform entry must explicitly state the upload video file path or `不上传视频`, the upload cover file path, the final title field, and the final copy or body source
- `platform-upload-map.md` or an equivalent per-platform upload matrix is mandatory; a publish thread must be able to open it and know exactly what to upload without inferring anything
- for article or note platforms that do not upload video, write `不上传视频` explicitly instead of leaving the video field blank
- do not classify 头条号 as article-only in a Seedance video campaign; default to video upload unless the package explicitly contains a separate 头条号图文派生稿
- for 头条号 in a Seedance video campaign, the platform-specific cover field must prefer the generated vertical `3:4` cover as the primary upload cover; the horizontal `4:3` cover is only a fallback unless the user explicitly overrides it
- verify target account name and account ID before browser-side upload
- final success must be judged from platform management lists, not only from compose-page button states
- when generating Hermes handoff files, use only Hermes-supported `scope` values: `all_platforms`, `social_only`, `video_focused`, or `wechat_channels_only`; do not write `all_supported_platforms_video_publish` unless the Hermes skill has been updated to support it
- the Hermes direct JSON package must include `campaignId`, `sourceThreadId`, `sourceCampaignId`, `sourceConfig`, `sourceContentRoot`, `receiptPath`, `scope`, and `platforms`
- the Hermes direct JSON `platforms` object must include only currently supported Hermes platforms: `bilibili`, `toutiao`, `zhihu`, `baijiahao`, `kuaishou`, `weibo`, and `wechat_channels`
- do not include `xiaohongshu` in the Hermes direct JSON package
- mark `douyin` as `unsupported_by_current_hermes_skill` outside the Hermes direct JSON `platforms` object; do not send it into Hermes publish testing
- each Hermes direct JSON platform entry must contain `title`, `description`, `videoPath`, and `coverPath`
- `videoPath` in Hermes direct JSON must use the publish-ready video, not the raw generated backup video
- `coverPath` in Hermes direct JSON must use the platform-appropriate vertical or horizontal prepared cover
- every ready-for-publish Hermes handoff file set must include `fingerprints` with `title_hash`, `body_core_hash`, `video_sha256`, and `cover_sha256` so Codex and Hermes can both perform duplicate prevention without relying on chat context
- `title_hash` should be a deterministic SHA-256 over normalized platform title strings; `body_core_hash` should be a deterministic SHA-256 over normalized platform description/body strings
- `video_sha256` must be the SHA-256 of the publish-ready video file; `cover_sha256` must be the SHA-256 of the canonical prepared cover, and include extra cover hashes when multiple cover ratios are used
- every ready-for-publish Hermes handoff file set must include `lock_dir` pointing to `/Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/automation/python-platform-takeover/state/publish-locks`
- the initial receipt must document the future per-platform receipt schema: `actor`, `actor_session_id`, `status`, `verified_by`, `lock_path`, and `submitted_at` / `published_at`
- `state/hermes-handoff/latest.json` must always point to the latest real `ready_for_publish` campaign only; never point it at test packages, smoke packages, `/tmp` packages, or scratch packages
- before creating or updating Hermes handoff files, hard stop if the receipt for the same campaign already has any platform record, or if the campaign/platform has already been published, submitted, or is under review
- do not reuse an old campaign receipt for a new Hermes handoff
- generating Hermes handoff files must not trigger real publishing, uploading, submit clicks, Xiaohongshu testing, or any modification under `/Users/baishangjituan/Documents/push`

Preferred output files in this workspace:

- `content-library/posts/shared/<campaign>-all-platform-publish-package.md`
- `content-library/posts/video/<campaign>-video-publish-package.md`

Windows-ready handoff rules for this repo:

- If the downstream publisher uses `automation/python-platform-takeover`, mirror the same final copy into `automation/python-platform-takeover/configs/content-package.local.yaml` or a dated `content-package.<campaign>.yaml`.
- Field mapping stays shared across macOS and Windows:
  - `platforms.douyin.title` / `description` = 抖音 `标题` / `文案`
  - `platforms.kuaishou.title` / `description` = 快手 `标题` / `文案`
  - `platforms.wechat_channels.title` / `description` = 视频号 `短标题` / `描述`
  - `platforms.weibo.title` / `description` = 微博视频 `标题` / `配文`
  - `platforms.baijiahao` / `toutiao` / `zhihu` / `xiaohongshu` = 各平台 `标题` / `正文或描述`
- On Windows, keep `assets.main_video`, `assets.cover_3_4`, and `assets.cover_4_3` as quoted absolute paths, preferably `C:/...`.
- On Windows, keep the same Hermes duplicate-prevention metadata intact: `fingerprints.title_hash`, `fingerprints.body_core_hash`, `fingerprints.video_sha256`, `fingerprints.cover_sha256`, plus `lock_dir` pointing at `automation/python-platform-takeover/state/publish-locks`. Do not strip or rewrite those keys during handoff.
- Keep the review evidence split on Windows exactly the same way: save internal findings in `latest-review.md` or `brief.json`, keep `video-prompt.txt` and publish copy audience-facing, and do not paste raw review wording into the dated YAML or platform text fields.
- If the `大陈 / AI员工 / 机器人小马` package uses the default female supporting role, keep `asset://asset-20260401123823-6d4x2` as a literal Seedance `reference_image` asset URI in the payload. Do not rewrite that item into a `C:/...` filesystem path.
- In the Windows upload matrix, every platform row must still name the exact upload video path or `不上传视频`, the exact cover path, and the final title/copy source. For Seedance video campaigns, 头条号 should point at the real video path by default instead of silently falling back to article-only assumptions.
- On Windows, `state/hermes-handoff/latest.json` must still point only at the newest real `ready_for_publish` campaign. Do not move that pointer to smoke-test packages, `/tmp` scratch packages, or validation-only packages just because they were the last files touched.
- Before handing the package to a Windows publish thread, run `.\scripts\social-publisher.ps1 validate-package <yaml>` and `.\scripts\social-publisher.ps1 receipt-status <yaml>` against the same campaign. If the receipt already contains any platform record, published state, submitted state, or under-review state, stop instead of regenerating or reusing the handoff.
- Do not mark the campaign `ready_for_publish` until the markdown publish package exists and `.\scripts\social-publisher.ps1 validate-package automation/python-platform-takeover/configs/content-package.local.yaml` passes with those final titles and descriptions.
- If the final YAML lives in a dated `content-package.<campaign>.yaml` instead of `content-package.local.yaml`, run the same PowerShell validation against that dated file before handing the package to publishing.

## Windows PowerShell Quick Use

Use the bundled PowerShell launcher when the skill mirror is synced onto a Windows machine:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.ps1 submit --payload C:/work/payload.json --dry-run
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.ps1 wait cgt-xxxx --download C:/work/output.mp4
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/build_cover_package.ps1 --video C:/work/final_video.mp4 --output-dir C:/work/cover-package --main-title 'AI员工上岗了' --subtitle '自动跑平台' --candidate-index 2 --tag '平台执行'
```

Windows path handling rules:

- Prefer quoted absolute paths.
- Prefer `C:/...` forward-slash paths in JSON payloads so they also stay valid on macOS hosts.
- Keep bundled Seedance asset references such as `asset://asset-20260401123823-6d4x2` unchanged; only local filesystem inputs should be converted to `C:/...` paths on Windows.
- The PowerShell launcher will try `.venv\\Scripts\\python.exe`, an active virtualenv, `py -3`, `python`, then an installed `uv` managed Python.

## macOS Quick Use

Use the bundled shell launcher when the skill mirror is synced onto a Mac:

```bash
bash /Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.sh submit --payload /Users/name/work/payload.json --dry-run
bash /Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.sh wait cgt-xxxx --download /Users/name/work/output.mp4
python3 /Users/name/.codex/skills/seedance-video-api/scripts/build_cover_package.py --video /Users/name/work/final_video.mp4 --output-dir /Users/name/work/cover-package --main-title 'AI员工上岗了' --subtitle '自动跑平台' --candidate-index 2 --tag '平台执行'
```

macOS path handling rules:

- Prefer quoted absolute paths.
- Prefer `python3` or a local virtualenv with Python `3.10+`.
- The shell launcher will try `./.venv/bin/python`, an active virtualenv, `python3`, `python`, then an installed `uv` managed Python.

## Bundled CLI And Cover Helpers

Primary script:

- `scripts/seedance_cli.py`
- `scripts/seedance_cli.sh`
- `scripts/seedance_cli.ps1`
- `scripts/init_cover_package.py`
- `scripts/extract_cover_candidates.py`
- `scripts/render_cover_package.py`
- `scripts/build_cover_package.py`
- `scripts/init_cover_package.ps1`
- `scripts/extract_cover_candidates.ps1`
- `scripts/render_cover_package.ps1`
- `scripts/build_cover_package.ps1`
- `scripts/invoke_seedance_script.ps1`

Primary commands:

```bash
python3 /Users/baishangjituan/.codex/skills/seedance-video-api/scripts/seedance_cli.py submit --payload /absolute/path/to/payload.json --dry-run
python3 /Users/baishangjituan/.codex/skills/seedance-video-api/scripts/seedance_cli.py submit --payload /absolute/path/to/payload.json --wait --download /absolute/path/to/output.mp4
python3 /Users/baishangjituan/.codex/skills/seedance-video-api/scripts/seedance_cli.py get cgt-xxxx
python3 /Users/baishangjituan/.codex/skills/seedance-video-api/scripts/seedance_cli.py wait cgt-xxxx --download /absolute/path/to/output.mp4
python3 /Users/baishangjituan/.codex/skills/seedance-video-api/scripts/seedance_cli.py download cgt-xxxx --last-frame --output /absolute/path/to/last_frame.png
```

Behavior notes:

- Local images and audio can use `local://...` and will be converted to Base64 data URIs automatically.
- Local video files are intentionally rejected because Ark `video_url.url` expects a public URL or `asset://...`.
- The script supports payload normalization for `text`, `image_url`, `video_url`, `audio_url`, and `draft_task`.
- The candidate-frame script uses local `ffmpeg` / `ffprobe` to extract stills and generate a contact sheet.
- The render script uses Pillow plus an auto-detected Chinese font file to output final delivery PNG covers.
- If the current shell Python lacks Pillow, the render script automatically re-runs under the Codex bundled Python runtime when that runtime is available.
- Do not edit the bundled CLI unless the user explicitly asks to change the skill itself.

## Templates

Bundled payload templates live under:

- `assets/examples/t2v_seedance_2_0.json`
- `assets/examples/t2v_seedance_2_0_fast.json`
- `assets/examples/i2v_first_frame_seedance_2_0.json`
- `assets/examples/multimodal_reference_seedance_2_0.json`
- `assets/examples/extend_single_seedance_2_0.json`
- `assets/examples/extend_bridge_seedance_2_0.json`

Use them as copy-and-edit starting points, not as files to overwrite in place.

## Extension And 30s Strategy

Seedance 2.0 and 2.0 Fast only output `4-15s` per task, so longer videos must be staged.

Use these rules:

- Single-video extension: pass one `reference_video` plus an extension prompt.
- Bridge extension: pass `2-3` `reference_video` clips and prompt the transition.
- For a practical `30s` result, prefer `10-12s` segments chained across multiple tasks.
- Do not try to put two 15-second clips into one extension request; official constraints cap total input reference-video duration at `15s`.
- Save and re-host generated clips quickly because task result URLs expire after `24h`.

See:

- `references/api-basics.md`
- `references/workflows.md`
- `references/cover-package.md`
- `references/cover-execution.md`

## Official Constraints To Remember

- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- Create task: `POST /contents/generations/tasks`
- Query task: `GET /contents/generations/tasks/{id}`
- `Seedance 2.0`: `doubao-seedance-2-0-260128`
- `Seedance 2.0 Fast`: `doubao-seedance-2-0-fast-260128`
- Output duration: `[4, 15]` seconds or `-1` for auto duration within supported range
- Seedance 2.0 / Fast do not support `1080p`
- Query data retention is short and result download URLs are temporary

## Reference Map

- `references/api-basics.md`: endpoint, model IDs, limits, and auth reminders
- `references/workflows.md`: practical recipes for t2v, i2v, multimodal, and extension
- `references/cover-package.md`: fixed cover output standard for multi-platform reuse after generation
- `references/cover-execution.md`: helper-script flow for brief, candidate frame extraction, and final cover rendering
