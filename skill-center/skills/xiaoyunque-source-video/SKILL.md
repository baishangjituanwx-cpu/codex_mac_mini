---
name: xiaoyunque-source-video
description: Use when Codex needs to generate, edit, monitor, download, or QA 小云雀 source videos for founder口播、方法型短视频、9:16竖屏源视频、title poster、封面制作专用文案、核心母题、核心判断. Generation must be handled only through the 小云雀 API integration / xyq-nest-skill; do not operate 小云雀 or 剪映网页版 in a browser for generation.
---

# XiaoYunque Source Video

## Current Rule

This is the workspace's 小云雀 source-video skill.

From now on, 小云雀 generation must be handled only through the API integration documented in:

- `https://bytedance.larkoffice.com/wiki/JUlowWl8Bi6X8fkTKrYc70zRnVc`
- official installed API skill: `/Users/baishangjituan/.codex/skills/xyq-nest-skill/SKILL.md`
- repo mirror Windows launchers: `skill-center/skills/xyq-nest-skill/scripts/*.ps1`

Do not use these old routes for generation:

- 小云雀 / 剪映网页版 manual operation
- Chrome tab takeover, sticky tabs, homepage locking, or browser polling
- Agent 模式 UI, integrated-agent thread UI, file picker upload, or asset-library selection
- Playwright/browser-use for 小云雀 generation
- manual extraction from webpage preview layers

Browser links returned by the API are only for user visibility. They are not the operating path.

## API Skill Contract

Use the official `xyq-nest-skill` scripts as the execution layer:

- submit or continue a run: `/Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/submit_run.py`
- poll a run: `/Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/get_thread.py`
- upload a local image/video asset: `/Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/upload_file.py`
- download generated artifacts: `/Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/download_results.py`

When preparing or documenting the Windows repo branch, the equivalent launchers are:

- `skill-center/skills/xyq-nest-skill/scripts/submit_run.ps1`
- `skill-center/skills/xyq-nest-skill/scripts/get_thread.ps1`
- `skill-center/skills/xyq-nest-skill/scripts/upload_file.ps1`
- `skill-center/skills/xyq-nest-skill/scripts/download_results.ps1`

Required environment:

- `XYQ_ACCESS_KEY`

Optional environment:

- `XYQ_OPENAPI_BASE`
- `XYQ_BASE_URL`

Default base URL is `https://xyq.jianying.com`.

Never hard-code or print the access key. If the key is missing, stop and ask the user to provide or configure `XYQ_ACCESS_KEY`; do not fall back to the web UI.

Windows note:

- set the key with `$env:XYQ_ACCESS_KEY = "..."` in PowerShell
- use quoted `C:/...` absolute paths for local files and output directories
- do not leave `/Users/...` examples in Windows handoff notes

The API endpoints used by the official scripts are:

- `POST /api/biz/v1/skill/submit_run`
- `POST /api/biz/v1/skill/get_thread`
- `POST /api/biz/v1/skill/upload_file`

The scripts authenticate with:

- `Authorization: Bearer <XYQ_ACCESS_KEY>`

## Execution Principles

The user-side agent is the API operator, not the creative engine.

When the task is actual XiaoYunque generation or editing:

1. Pass the user's creation/editing request to the API as the `message`.
2. If the user supplied local image/video references, upload each supported file first and pass returned `asset_id` values to `submit_run.py`.
3. Do not manually expand, rewrite, translate, or over-engineer the prompt unless the user explicitly asks for a prompt package.
4. Do not split one creative request into multiple artificial runs unless the user asks for separate outputs.
5. Show the returned `web_thread_link` when available, but continue operating through API polling.
6. Poll `get_thread.py` with `thread_id`, `run_id`, and `after_seq`.
7. If the API asks a clarification question, show it to the user and wait. Continue in the same `thread_id` after the user answers.
8. When generated artifact URLs appear, download them with `download_results.py` and report the local file paths.
9. QA the downloaded source video before any cover or publishing handoff.

## Standard API Workflow

For text-to-video or direct generation:

1. Ensure `XYQ_ACCESS_KEY` is available.
2. Run `submit_run.py --message "<user request>"`.
3. Capture `thread_id`, `run_id`, and `web_thread_link`.
4. Poll `get_thread.py --thread-id <thread_id> --run-id <run_id> --after-seq <seq>` about every 10 seconds.
5. Continue until the run completes, fails, is cancelled, or asks the user for input.
6. Extract artifact URLs from the returned messages/content.
7. Download artifacts into a task-specific local output directory.
8. QA results and hand off to cover/publishing skills if needed.

For reference image/video generation or editing:

1. Validate each local reference file exists.
2. Upload each image/video with `upload_file.py`.
3. Submit the original user instruction with `--asset-ids <asset_id...>`.
4. Follow the same polling, download, and QA path.

For continuing an existing XiaoYunque task:

1. Reuse the known `thread_id`.
2. Run `submit_run.py --message "<new user instruction>" --thread-id <thread_id>`.
3. Poll the new `run_id`.

## Founder-IP Prompt Package Mode

Prompt-only mode is still allowed when the user asks for a 小云雀 prompt, refined prompt, or reusable founder-IP prompt package rather than asking Codex to generate via API.

In prompt-only mode:

1. Read `references/prompt-template.md`.
2. Preserve the workspace's founder-IP standards.
3. Output a package that can be sent as the API `message` field, not pasted into a webpage.

Default output order:

1. `主题文案`
2. `封面制作专用文案`
3. `核心母题`
4. `核心判断`
5. `建议口播内容`
6. one API-message-ready prompt block
7. a short self-check list when QA is relevant
8. when available, one short `复盘倾向说明`

If there is a recent review under `content-library/logs/review/`, read the latest relevant review first. When it includes `下一批小云雀视频高占比倾向`, treat that block as the generator-agnostic core brief before adapting it to XiaoYunque API wording.

## Founder Video Standards

Default target:

- duration about 30 seconds unless the user requests otherwise
- ratio `9:16`
- realistic office, meeting-room, shop, product, or business setting as appropriate
- Chinese spoken delivery
- single-line subtitles
- each subtitle line no more than 8 Chinese characters or an equally short phrase

Default founder-IP role rules:

- 大陈 is the main speaker and visual anchor
- 小丽 is an assistant or brief support role
- do not frame them as dual leads
- if identity drift appears, reduce 小丽 shots before weakening 大陈

Current local reference assets:

- 大陈: `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/大陈.jpg`
- 小丽: `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/小丽.png`

Fallback local reference assets:

- `/Users/baishangjituan/Downloads/素材/小云雀/大陈.jpg`
- `/Users/baishangjituan/Downloads/素材/小云雀/小丽.png`

Windows handoff equivalent:

- `C:/Users/<name>/Downloads/素材/小云雀/人物素材/大陈.jpg`
- `C:/Users/<name>/Downloads/素材/小云雀/人物素材/小丽.png`
- `C:/Users/<name>/Downloads/素材/小云雀/大陈.jpg`
- `C:/Users/<name>/Downloads/素材/小云雀/小丽.png`

When API generation needs these reference images, upload the real local files with `upload_file.py` and pass the returned `asset_id` values. Do not upload them through a browser file picker.

Visual rules:

- no static podium or stage speech unless explicitly requested
- no ad-film or launch-event feeling for founder method videos
- keep 大陈 in medium-close or half-body framing when 大陈 is the subject
- keep the top of the head fully visible
- preserve at least one clear frame that can later be used for cover capture

## QA Before Handoff

The source video is not qualified unless all four checks pass:

- the person still reads as the intended subject
- the scene matches the intended business setting
- subtitles are short enough for mobile reading
- the video contains a clear cover-ready frame

Regenerate or ask the API for a revision instead of patching downstream if you see:

- face drift
- glasses, hair, or face shape instability
- cropped head
- too many full-body or long-distance shots
- weak scene realism
- subtitles that are too long
- no usable frame for a real cover screenshot

## Handoff After Export

After a usable video artifact is downloaded:

1. QA the source video.
2. Build one local `3:4` vertical cover and one local `4:3` horizontal cover when this is a founder/publishing workflow.
3. Put a vertical title poster into the first 1 to 2 seconds if the platform is cover-unstable.
4. Only then move into platform publishing.

Before any repost or retry, check the target platform's management list for duplicates first.

## Related Skills

- Use `$xyq-nest-skill` as the API execution skill when it is available in the current session.
- Use `$platform-cover-ops` after generation when cover packaging or title-poster design is needed.
- Use `$social-publish-automation` only for browser-side platform publishing or draft resume, not for XiaoYunque generation.
- Use `$dachen-founder-flywheel` for broader founder-IP topic planning.
- Use `$data-review` when the next video direction should come from a fresh post-publish review.

## References

- `references/prompt-template.md` keeps the founder-IP prompt standard.
- `references/source-video-playbook.md` records the API-only source-video playbook.
