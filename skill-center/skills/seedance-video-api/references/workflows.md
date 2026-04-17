# Seedance Workflow Recipes

## 1. Text To Video

Use:

- `assets/examples/t2v_seedance_2_0.json`
- `assets/examples/t2v_seedance_2_0_fast.json`

Recommended flow:

1. Copy a template into the project workspace.
2. Replace the prompt.
3. Run `submit --dry-run`.
4. Run `submit --wait --download ...`.

## 2. First-Frame Image To Video

Use:

- `assets/examples/i2v_first_frame_seedance_2_0.json`

Notes:

- Keep the image local with `local://...` or switch to a public image URL.
- Use `return_last_frame=true` if the user wants a future extension anchor.

## 3. Multimodal Reference Video

Use:

- `assets/examples/multimodal_reference_seedance_2_0.json`

Notes:

- This is for reference-image / reference-video / reference-audio style control.
- Do not mix first-frame / last-frame mode with multimodal reference mode.

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

Why:

- One task cannot output more than `15s`
- One extension request cannot exceed `15s` total input reference-video duration
- Chaining shorter segments is more stable than trying to max every clip to `15s`
