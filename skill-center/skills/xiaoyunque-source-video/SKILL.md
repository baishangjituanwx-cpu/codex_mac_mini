---
name: xiaoyunque-source-video
description: Use when Codex needs to plan, prompt, QA, or operate 小云雀 / 剪映网页版 as an upstream short-video generator for founder口播、方法型短视频、9:16竖屏源视频、storyboard 调整、`final_video.mp4` 导出，或为小云雀任务输出主题文案、核心母题、核心判断、title poster 规则和标准化提示词。
---

# XiaoYunque Source Video

## Overview

Use this skill when the main task is to make the upstream source video correct in 小云雀 first.

In this workspace, 小云雀 is:

- the upstream source-video generator
- the place to make the reusable vertical master video
- not the final publish confirmation layer

Do not treat “小云雀已经出片” as “已经可以直接发平台”.

When the user only asks for a prompt package and does not need browser operation yet, still use this skill. In prompt-only mode, the default output should follow the standard in [references/prompt-template.md](references/prompt-template.md).

If the task is mainly about:

- cover packaging or title-poster design, also use [$platform-cover-ops](/Users/baishangjituan/.codex/skills/platform-cover-ops/SKILL.md)
- browser-side publishing or draft resume, also use [$social-publish-automation](/Users/baishangjituan/.codex/skills/social-publish-automation/SKILL.md)
- real browser interaction inside 小云雀 / 剪映网页版, also use [$playwright](/Users/baishangjituan/.codex/skills/playwright/SKILL.md) or [$playwright-interactive](/Users/baishangjituan/.codex/skills/playwright-interactive/SKILL.md)
- broader founder-IP topic planning across platforms, also use [$dachen-founder-flywheel](/Users/baishangjituan/.codex/skills/dachen-founder-flywheel/SKILL.md)
- when the next video prompt should come from a fresh post-publish review, also use [$data-review](/Users/baishangjituan/.codex/skills/data-review/SKILL.md)

## Core Workflow

### 0. Lock the correct homepage first

The correct XiaoYunque task-entry URL for this workspace is:

- `https://xyq.jianying.com/home?tab_name=home`

Before doing anything else in Chrome:

1. Check whether any existing Chrome tab is already open at the exact URL above
2. If that tab exists, take over that tab directly
3. Do not open a duplicate tab when the correct tab already exists
4. If no tab is open at that exact URL, create a new Chrome tab
5. Open the exact URL above in that new tab
6. Only then start the XiaoYunque video workflow

If the currently visible XiaoYunque page is an old `integrated-agent` thread URL instead of the exact homepage above:

- do not keep using that old thread as the entry point
- open or switch to the exact homepage URL first
- only re-enter a generation thread after the new task has been created from the correct homepage

This rule has priority over convenience links, old thread URLs, and previously opened sub-pages.

### 0.1 Keep one sticky working tab

Once you have taken over one XiaoYunque Chrome tab for the current task:

1. Treat that tab as the sticky working tab for both task creation and progress monitoring
2. On every later step, first re-bind or re-take over that same tab
3. Do not directly create another new XiaoYunque tab if the sticky working tab still exists
4. If the sticky working tab has navigated from homepage into a generation thread, keep using that same tab for status checks, retries, downloads, and the next button click
5. Only create a new XiaoYunque tab if the sticky working tab has been closed, crashed, or is no longer recoverable

This means:

- starting a new task should reuse the already-taken-over tab
- monitoring generation progress should reuse the already-taken-over tab
- retrying after a failure should reuse the already-taken-over tab when possible
- do not scatter one XiaoYunque task across multiple new tabs

### 0.2 Auto-check progress after submission

After a XiaoYunque generation has been successfully submitted:

1. Immediately switch from submit mode into progress-monitor mode
2. Keep re-binding or re-taking over the same sticky working tab
3. Do not wait for the user to remind you to check progress
4. Keep polling the page until a real terminal state appears

Recommended polling rhythm:

- first 1 minute after submission: check about every 5 to 10 seconds
- during active generation or long planning stages: check about every 15 to 30 seconds
- during long composite or final-video stages: check about every 30 to 60 seconds

When polling, always read:

- current URL
- visible page status text
- whether the thread is still in the same task
- whether there is a new actionable button

Treat these as normal in-progress states rather than failures:

- `正在加载技能`
- `任务规划`
- `任务规划完成`
- `生成创意`
- `正在理解素材`
- `生成分镜`
- `参考素材`
- `视频合成`
- `最终视频`
- `分镜片段完成`

Treat these as terminal success signals:

- `final_video.mp4`
- `最终视频合成`
- `最终视频`
- a clear downloadable final asset
- a visible result area that confirms final video is ready

Treat these as terminal failure signals:

- `执行失败`
- `暂不支持人脸`
- `素材不可用`
- `请修改诉求后再试`
- `小云雀遇到了一些问题`

Special bridge handling:

- if the browser bridge temporarily returns `about:blank` or an empty body, do not mark the task failed
- first re-bind the same Chrome tab again
- then re-check the actual XiaoYunque tab URL and thread before deciding the state

If the task is still in progress:

- continue polling automatically
- do not stop just because one check shows no new text
- only report back when there is a milestone, a blocker, or a completed artifact

### 1. Lock the package before generating

Before touching the UI, lock these four things:

- one核心判断句
- one reusable `9:16` vertical source video
- one single-line subtitle rule
- one cover handoff route

Good judgment skeletons in this workspace include:

- `第一步就做错了`
- `别先裁人`
- `先拆流程`
- `先替劳动`

Emotion can be used as the first 2 to 3 second hook, but the video must quickly return to a founder judgment and method.

### 1.1 Agent mode is mandatory for this workspace

For the current XiaoYunque workflow in this workspace:

1. Prefer `Agent 模式` as the required primary route
2. Do not silently switch to `动作模仿`, `照片跟我动`, or other non-Agent routes just because they look easier
3. If the user explicitly says this round must stay in Agent mode, keep the whole attempt inside Agent mode
4. If an Agent attempt fails because the uploaded pictures are rejected, stop and report the exact page feedback
5. After that exact feedback appears, ask the user for replacement images and wait for those new files before retrying

This means:

- do not auto-fallback away from Agent mode
- do not continue a failed Agent attempt with another generation path unless the user explicitly changes the rule
- when the page says the current image materials are unavailable, incompatible, or unsupported, the correct next step is to collect new images from the user

### 2. Verify reference assets first

The 2026-04-10 founder prompt standard was written against these reference-image paths:

- 大陈: `/Users/z/Downloads/新媒体素材/大陈.jpg`
- 小丽: `/Users/z/Downloads/新媒体素材/小丽.png`

If those paths do not exist on the current machine, fall back in this order:

- `/Users/baishangjituan/Downloads/素材/小云雀/大陈.jpg`
- `/Users/baishangjituan/Downloads/素材/小云雀/小丽.png`
- `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/大陈.jpg`
- `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/小丽.png`

Current verified local reference images for this account:

- 大陈: `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/大陈.jpg`
- 小丽: `/Users/baishangjituan/Downloads/素材/小云雀/人物素材/小丽.png`

Current preferred local upload root:

- `/Users/baishangjituan/Downloads/素材/小云雀`

If root-level aliases exist under that upload root, prefer them first for file-picker convenience:

- `/Users/baishangjituan/Downloads/素材/小云雀/大陈.jpg`
- `/Users/baishangjituan/Downloads/素材/小云雀/小丽.png`

Role rules:

- 大陈 is the main speaker and visual anchor
- 小丽 is an assistant or brief support role
- do not frame them as dual leads
- if identity drift appears, reduce 小丽 shots before weakening 大陈

If a path is missing, search locally by filename before asking the user to re-provide assets.

When XiaoYunque needs image materials:

1. Prefer `+ -> 本地上传`
2. Prefer files under `/Users/baishangjituan/Downloads/素材/小云雀`
3. If the required files are inside subfolders under that root, use those real files directly
4. Only fall back to `从资产库选择` when local upload is unavailable or the local files are missing
5. Do not prefer asset-library items over valid local files when both are available

### 2.1 Prompt output standard is mandatory

Whenever the task asks for a 小云雀 prompt, a refined prompt, or a reusable founder-IP prompt package:

1. Read [references/prompt-template.md](references/prompt-template.md)
2. Follow that document's fixed rules before adding topic-specific details
3. Keep 大陈 as the absolute lead and 小丽 as a brief support role
4. Keep the opening `0 to 2 seconds` as a readable title poster with 大陈 front-facing
5. Keep subtitles to a single line with at most `8` Chinese characters per line
6. If the workspace already has a recent review under `content-library/logs/review/`, read the latest relevant review first
7. When that review includes `下一批小云雀视频高占比倾向`, treat it as a priority input instead of optional inspiration
8. Do not reuse a weak title-poster phrase from the previous batch if the review explicitly marks it abstract or low-conversion

In prompt-only mode, output in this order unless the user asks for a different format:

1. `主题文案`
2. `核心母题`
3. `核心判断`
4. one full prompt block ready to paste into 小云雀
5. a short self-check list when QA is relevant
6. when available, one short `复盘倾向说明`

### 3. Follow the stable generation order

Use this order:

1. Create a new task
2. Write the prompt
3. Upload reference images
4. Generate creative or storyboard first
5. Correct ratio, subtitles, BGM, and scene direction
6. Generate reference assets
7. Generate storyboard video
8. Generate final composite video
9. Download and QA `final_video.mp4`

If the direction is wrong at storyboard stage, fix the storyboard before pushing to final video generation.

### 4. Enforce the hard rules

Default target:

- duration about 30 seconds
- ratio `9:16`
- realistic office or meeting-room setting
- Chinese spoken delivery
- single-line subtitles only
- each subtitle line no more than 8 Chinese characters or an equally short phrase

Default visual rules:

- no static podium or stage speech
- no ad-film or launch-event feeling
- keep 大陈 in medium-close or half-body framing
- keep the top of the head fully visible
- preserve at least one clear frame that can later be used for cover capture

### 5. QA the source video before handoff

The source video is not qualified unless all four checks pass:

- the person still reads as 大陈
- the scene matches the intended business setting
- the subtitles are short enough for mobile reading
- the video contains a clear cover-ready frame

Regenerate the source video instead of patching downstream if you see:

- face drift
- glasses, hair, or face shape instability
- cropped head
- too many full-body or long-distance shots
- weak office realism
- subtitles that are too long
- no usable frame for a real cover screenshot

### 6. Hand off immediately after export

After `final_video.mp4` is available:

1. QA the source video
2. build one local `3:4` vertical cover and one local `4:3` horizontal cover
3. put the vertical title poster into the first 1 to 2 seconds if the platform is cover-unstable
4. only then move into platform publishing

Before any repost or retry, check the target platform's management list for duplicates first.

## Download Clues

Common useful XiaoYunque artifacts:

- storyboard JSON
- reference assets
- storyboard video
- final composite `final_video.mp4`

Common valid download signals:

- `final_video.mp4` in the asset list
- `sandbox:///workspace/assets/.../final_video.mp4`
- a real CDN video URL behind the preview layer

## Reference Files

- Use [references/source-video-playbook.md](references/source-video-playbook.md) for the full end-to-end operating playbook, failure handling, and the release checklist.
- Use [references/prompt-template.md](references/prompt-template.md) for the reusable prompt skeleton and the current default person rules.
