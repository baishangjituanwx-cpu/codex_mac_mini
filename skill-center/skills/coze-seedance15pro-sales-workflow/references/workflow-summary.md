# Workflow Summary

## Export Identity

- export type: `Workflow`
- workflow name: `coze_seedance15pro_test_sales`
- workflow id: `7618839501548896271`
- description: `sales`

## Node Map

### 1. Start node `100001`

Purpose:

- define the inputs required to launch the workflow

Declared outputs:

- `duration`: float, required
- `generate_audio`: boolean, required
- `image`: image, optional
- `image_url`: string, optional
- `prompt`: string, required
- `ratio`: string, required
- `resolution`: string, required

### 2. Video generation node `148755`

Purpose:

- run the actual Seedance video generation

Important settings:

- type: `video_generation`
- model: `doubao-seedance-1.5-pro`
- generate mode: `image2Video`
- camera fixed: `false`
- seed: `-1`
- watermark: `false`
- timeout: `360000`

Mapped inputs:

- `prompt` <- start.`prompt`
- `image_url` <- start.`image_url`
- `duration` <- start.`duration`
- `ratio` <- start.`ratio`
- `resolution` <- start.`resolution`
- `generate_audio` <- start.`generate_audio`
- `image` <- start.`image`

Frame anchoring:

- `firstFrame` references start.`image`
- `lastFrame` references start.`image`

Declared outputs:

- `msg`: string
- `video`: video

### 3. End node `900001`

Purpose:

- return the generated `video`

Returned variable:

- `video` <- node `148755`.`video`

## Interpreting This Workflow

This export is a minimal wrapper around one model call.

## Two Explicit Modes

### 文生视频

Use:

- `prompt`
- `duration`
- `ratio`
- `resolution`
- `generate_audio`

Do not provide image inputs unless the task should become 图生视频.

### 图生视频

Use:

- `prompt`
- `image_url` in the live runner
- or archived `image` / `image_url` workflow inputs when editing the raw YAML contract

Treat the image as the visual anchor for motion generation.

What it already does:

- accepts a prompt
- accepts an image or image URL pathing input
- accepts duration, ratio, resolution, and audio toggle
- produces a final video output
- can be invoked through the official Coze run API in sync mode or async mode

What it does not show:

- no moderation branch
- no prompt templating node
- no multiple scene stages
- no validation or retry logic beyond the node's own settings
- no cover generation, subtitle polishing, or publish step

## Suggested Input Shape

When you need to prepare a run request or explain how to fill the workflow, map the request into something like:

```yaml
prompt: "Describe the intended video clearly"
duration: 12
generate_audio: true
image: "<uploaded image asset>"
image_url: ""
ratio: "9:16"
resolution: "720p"
```

Use either a local uploaded `image` object, an `image_url`, or both if the calling system supports it.
