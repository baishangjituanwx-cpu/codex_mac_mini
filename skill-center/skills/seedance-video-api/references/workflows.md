# Seedance Workflow Recipes

## 1. Text To Video

Use:

- `assets/examples/t2v_seedance_2_0.json`
- `assets/examples/t2v_seedance_2_0_fast.json`

Recommended flow:

1. Copy a template into the project workspace.
2. Replace the prompt and save the working artifacts: `brief.json`, `video-prompt.txt`, and the normalized `seedance_payload.json`.
3. Run `submit --dry-run`.
4. Run `submit --wait --download ...`.
5. If subtitles are wrong, regenerate; do not local-patch subtitles and still call the asset publish-ready.
6. Build the mandatory post-generation cover package from the finished video.
7. Build the video publish package with platform-specific titles and concrete copy.
8. Save a per-platform upload matrix such as `platform-upload-map.md` that explicitly lists, for every platform, the upload video path or `不上传视频`, the upload cover path, the final title, and the copy or body source file.
9. If one generated master video will be reused across all video platforms, write that explicitly in the upload matrix instead of making the publish thread infer it.
10. If browser-side publish is the next step, also save a `publish-plan.md` or `publish-plan.json` plus a `browser-use-checklist.md`.
11. If the platform upload asset differs from the raw generated video, keep both `raw_video` and `publish_video` in the package and mark which one should be uploaded.
12. For Douyin, validate that the title is within `20` visible Chinese characters, the description lead stays within `18`, and the two do not share a repeated `3+` character chunk.
13. Do not call the campaign `ready_for_publish` until the cover package, publish-copy package, upload matrix, and publish-plan artifacts all exist.

## 2. First-Frame Image To Video

Use:

- `assets/examples/i2v_first_frame_seedance_2_0.json`

Notes:

- Keep the image local with `local://...` or switch to a public image URL.
- Use `return_last_frame=true` if the user wants a future extension anchor.
- If this clip is headed for multi-platform publishing, prepare the post-generation cover package immediately after the final video lands.
- If this clip is headed for multi-platform publishing, also prepare the video publish package immediately after the cover package lands.

## 3. Multimodal Reference Video

Use:

- `assets/examples/multimodal_reference_seedance_2_0.json`

Notes:

- This is for reference-image / reference-video / reference-audio style control.
- Do not mix first-frame / last-frame mode with multimodal reference mode.
- The publishing-ready deliverable is `video + cover package + publish-copy package`, not `video only`.
- For the `大陈 / AI员工 / 机器人小马` line, include the female supporting role by default with `asset://asset-20260401123823-6d4x2` as an additional `reference_image`, unless the user explicitly excludes that role.
- When multiple real-person references are present, lock each person's identity separately; do not let the female supporting role merge with 大陈, disappear into the background, or become a generic actor.

Required extra payload item for the female supporting role in the current founder-office video line:

```json
{
  "type": "image_url",
  "role": "reference_image",
  "image_url": {
    "url": "asset://asset-20260401123823-6d4x2"
  }
}
```

## 4. Single-Clip Extension

Use:

- `assets/examples/extend_single_seedance_2_0.json`

Pattern:

- Prompt describes how to continue or prepend around `视频1`
- One `reference_video`
- Output typically contains overlapping tail continuity, so plan for trimming

Good prompt shape:

```text
向后延长视频1，镜头继续穿过展厅长廊，光线逐渐变暗，最后停在一幅巨大的油画前。
```

## 5. Multi-Clip Bridge Extension

Use:

- `assets/examples/extend_bridge_seedance_2_0.json`

Pattern:

- `2-3` reference videos
- Prompt explicitly says how to move from `视频1` to `视频2` and optionally `视频3`

Good prompt shape:

```text
视频1中的拱形窗户打开，进入美术馆室内，接视频2，之后镜头进入画内，接视频3。
```

## 6. Practical 30s Plan

Do not aim for a single 30-second task.

Prefer:

1. Generate clip A: `10-12s`
2. Extend or continue into clip B: `10-12s`
3. Extend or continue into clip C: `10-12s`
4. Trim overlaps
5. Stitch externally with ffmpeg or an editor
6. Extract the best final still and export `3:4` + `4:3` PNG covers

Why:

- One task cannot output more than `15s`
- One extension request cannot exceed `15s` total input reference-video duration
- Chaining shorter segments is more stable than trying to max every clip to `15s`

## 7. Mandatory Post-Generation Cover Step

When the video is intended for downstream publishing, do not stop at the downloaded `mp4`.

Always add:

1. one `1080x1440` vertical PNG cover
2. one `1440x1080` horizontal PNG cover
3. both derived from a clean frame inside the final video
4. both following the lower-third title treatment in `cover-package.md`
5. shortlist candidate frames first if the final video has multiple usable close-up shots
6. render the final cover PNGs from the chosen candidate still
7. if the process needs repeatability or handoff, follow `cover-execution.md`

## 8. Mandatory Post-Generation Publish Copy Step

If the user says `内容包`, `可发布`, `准备发平台`, or anything equivalent, the work is still incomplete after the cover package.

Also generate one video publish package with concrete copy:

1. 抖音 `标题` + `文案`
2. 快手 `标题` + `文案`
3. 视频号 `短标题` + `描述`
4. 微博视频 `标题` + `配文`
5. B站 `标题` + `简介` when the campaign also goes to B站

Rules:

- these fields must be paste-ready final copy, not placeholders
- generate the package only after reading the latest completed multi-platform data review for this content line
- use that review as the primary evidence source for title angle, opening hook, keep / cut / retest guidance, and platform-specific wording
- if the latest review says `未完成内容级核验`, do not fabricate performance claims; carry that limitation into the package wording and next-step notes
- keep one unified topic but adapt title tone by platform
- for 视频号, treat `短标题` and `描述` as mandatory paired fields
- for 抖音, avoid `标题` and `文案首句` collapsing into the same phrase
- add a per-platform upload matrix so any downstream publish thread can see the exact video file, exact cover file, exact title, and exact copy to use
- if a platform does not upload video, state `不上传视频` explicitly instead of leaving the field implicit
- if all video platforms reuse the same generated master video, state that explicitly in the package rather than assuming the publisher will infer it
- in a Seedance video campaign, treat 头条号 as a video publish target by default; only mark it `不上传视频` when the user explicitly asks for a 头条图文派生稿
- if browser-side publishing has completed, save a final verification artifact such as `final-verify.json`
- if article / note platforms are in scope, continue with their正文包 as a separate downstream step
- on Windows handoff, copy the same final fields into `automation/python-platform-takeover/configs/content-package.local.yaml` or a dated `content-package.<campaign>.yaml`
- treat `platforms.wechat_channels.title` as 视频号 `短标题` and `platforms.wechat_channels.description` as 视频号 `描述`
- on Windows handoff, keep `latest-review.md` or `brief.json` as the internal review-evidence note and keep `video-prompt.txt`, platform titles, and platform copy audience-facing; do not paste raw data-review wording into the dated YAML or downstream publish text fields
- on Windows handoff, if the current `大陈 / AI员工 / 机器人小马` package keeps the default female supporting role, preserve the extra `reference_image` item as `asset://asset-20260401123823-6d4x2`; do not rewrite that payload field into a local `C:/...` path
- on Windows handoff, keep every upload-matrix row explicit: quoted `C:/...` video path or `不上传视频`, quoted `C:/...` cover path, final title field, and final copy source; for Seedance video campaigns, 头条号 should keep the real video path unless the package explicitly includes a separate 图文派生稿
- on Windows handoff, preserve Hermes duplicate-prevention metadata exactly as generated: `fingerprints.title_hash`, `fingerprints.body_core_hash`, `fingerprints.video_sha256`, `fingerprints.cover_sha256`, and `lock_dir = automation/python-platform-takeover/state/publish-locks`
- on Windows handoff, keep `state/hermes-handoff/latest.json` pointed only at the newest real `ready_for_publish` campaign; never repoint it to a smoke-test package, `/tmp` scratch package, or other validation-only handoff
- on Windows handoff, run `.\scripts\social-publisher.ps1 validate-package <yaml>` and `receipt-status <yaml>` before publish follow-up; if the receipt already shows any live platform record or submitted / under-review state, stop instead of reusing the handoff
- do not call the campaign `ready_for_publish` until the markdown publish package exists and `.\scripts\social-publisher.ps1 validate-package ...` passes against the finished YAML

Default naming:

- `cover-vertical-3x4.png`
- `cover-horizontal-4x3.png`
