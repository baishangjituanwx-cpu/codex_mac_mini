---
name: coze-seedance15pro-sales-workflow
description: Use when Codex needs to inspect, explain, adapt, parameterize, or locally run the configured Coze workflow for Seedance 1.5 Pro video generation, especially when the task mentions Coze, Seedance 1.5 Pro, `doubao-seedance-1.5-pro`, workflow YAML exports, `workflow_id`, PAT token configuration, or the specific inputs `prompt`, `image`, `image_url`, `duration`, `ratio`, `resolution`, and `generate_audio`.
---

# Coze Seedance15pro Sales Workflow

## Overview

Use this skill as both:

- the reference layer for one archived exported Coze workflow
- the local execution layer for the currently configured Coze workflow runner

Archived export:

- workflow name: `coze_seedance15pro_test_sales`
- workflow mode: `workflow`
- core model: `doubao-seedance-1.5-pro`
- main job: generate a video from prompt, with optional image input

Current local runtime configuration:

- workflow id is stored in [config.json](config.json)
- PAT is resolved from macOS Keychain first, then optional environment variable
- local runner is [scripts/run_workflow.py](scripts/run_workflow.py)
- local runner now supports both sync runs and official async runs with history polling

Treat this as a structured skill that helps Codex:

- understand the exact exported workflow structure
- explain what inputs the workflow expects
- prepare a correct invocation package
- adapt the workflow YAML or summarize what should be changed
- run the currently configured workflow from the local machine when asked

If the task is about general AI video generation outside this exact Coze export, prefer [$sora](/Users/baishangjituan/.codex/skills/sora/SKILL.md). If the task is about upstream founder short-video planning, also consider [$xiaoyunque-source-video](/Users/baishangjituan/.codex/skills/xiaoyunque-source-video/SKILL.md).

## Core Workflow

### 1. Confirm the task matches this exact export

Use this skill when the user is talking about:

- this exported zip or YAML
- Coze workflow imports or edits
- Seedance 1.5 Pro video generation in Coze
- the parameter contract for this workflow
- local Coze workflow execution with workflow ID plus PAT

Do not use this skill as the default for unrelated video tools or platform publishing work.

### 2. Choose the mode first

This skill has two explicit modes:

- `文生视频`:
  use `prompt` without `image_url`
- `图生视频`:
  use `prompt` with `image_url`

Always classify the request into one of those two modes before preparing inputs or running the workflow.

### 3. Read the parameter contract

This workflow's start node defines these inputs:

- required `prompt` as string
- required `duration` as float
- required `ratio` as string
- required `resolution` as string
- required `generate_audio` as boolean
- optional `image` as image
- optional `image_url` as string

The workflow returns:

- `video`

Before proposing any run or edit, make sure the user's request maps cleanly onto those fields.

For the local runner:

- `文生视频` supports:
- `prompt`
- `duration`
- `ratio`
- `resolution`
- `generate_audio`

- `图生视频` supports:
- `prompt`
- `image_url`
- support `duration`
- support `ratio`
- support `resolution`
- support `generate_audio`
- optional `bot_id`
- optional async execution with Coze run-history polling

The archived `image` object input still exists in the original workflow contract, but the local CLI runner currently uses `image_url` rather than uploading a raw Coze image object.

### 4. Understand the generation node behavior

The exported workflow uses one `video_generation` node with these important characteristics:

- model: `doubao-seedance-1.5-pro`
- mode: `image2Video`
- `prompt` comes directly from start input
- `image`, `image_url`, `duration`, `ratio`, `resolution`, and `generate_audio` all come directly from start input
- `firstFrame` and `lastFrame` both reference the same `image` input
- `watermark` is `false`
- `seed` is `-1`
- timeout is `360000 ms`

This means the workflow is currently a thin parameter wrapper around one Seedance generation step, not a multi-stage post-processing pipeline.

### 5. Apply safe interpretation rules

When helping with this workflow:

- treat `prompt` as the main creative control
- in `文生视频`, do not invent image inputs unless the user asks for image-guided generation
- in `图生视频`, treat `image_url` as the visual anchor
- treat archived `image` as part of the workflow contract, but treat `image_url` as the current live runner path
- do not invent hidden inputs that are not present in the exported YAML
- if the user asks for a new capability, clearly say it requires editing the workflow rather than pretending it already exists
- if the user asks to update workflow ID or PAT, change [config.json](config.json) and the PAT source instead of editing the archived export files blindly

### 6. Route the request correctly

- For “what does this workflow do”:
  summarize the nodes and parameter map
- For “how do I fill it”:
  first classify into `文生视频` or `图生视频`, then produce a clean payload
- For “how should I modify it”:
  point to the exact node fields that need changing
- For “turn this into a better video prompt”:
  generate prompt text, but keep it compatible with this workflow's existing input contract
- For “run it now”:
  use `python3 scripts/run_workflow.py` with the configured runtime and avoid changing the archived export unless the user explicitly asks

## Practical Notes

- The export currently contains only:
- one manifest file
- one workflow YAML
- one start node
- one video generation node
- one end node

- The workflow description is only `sales`, so do not assume richer business logic than the YAML actually contains.
- Because the workflow is so small, most changes the user asks for will likely require editing the single `video_generation` node or the start-node input schema.
- The archived export ID can differ from the currently configured runtime workflow ID. Treat [references/exported-workflow.yaml](references/exported-workflow.yaml) as historical source material, and [config.json](config.json) as the live runtime target.

## Local Runner

Inspect runtime settings without printing secrets:

```bash
python3 /Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/scripts/run_workflow.py --print-config
```

Run the configured workflow:

```bash
python3 /Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/scripts/run_workflow.py \
  --prompt "一只可爱的小猫在草地上玩耍" \
  --duration 5 \
  --ratio "16:9" \
  --resolution "720p"
```

### 文生视频

Use this shape:

```json
{
  "prompt": "描述要生成的视频",
  "duration": 5,
  "ratio": "16:9",
  "resolution": "720p",
  "generate_audio": true
}
```

### 图生视频

Use this shape:

```json
{
  "prompt": "描述要生成的视频",
  "image_url": "https://example.com/first-frame.jpg",
  "duration": 5,
  "ratio": "9:16",
  "resolution": "720p",
  "generate_audio": true
}
```

Image-to-video via URL:

```bash
python3 /Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/scripts/run_workflow.py \
  --prompt "人物缓缓转头微笑" \
  --image-url "https://example.com/first-frame.jpg" \
  --duration 5 \
  --ratio "9:16" \
  --resolution "720p"
```

Async run with history polling:

```bash
python3 /Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/scripts/run_workflow.py \
  --prompt "人物缓缓转头微笑" \
  --image-url "https://example.com/first-frame.jpg" \
  --duration 5 \
  --ratio "9:16" \
  --resolution "720p" \
  --async
```

## References

- Use [references/workflow-summary.md](references/workflow-summary.md) for the distilled node-by-node explanation and the input/output contract.
- Use [references/exported-workflow.yaml](references/exported-workflow.yaml) for the exact exported workflow YAML.
- Use [references/manifest.yml](references/manifest.yml) for the original Coze export manifest.
- Use [references/runtime-config.md](references/runtime-config.md) for the live runtime workflow ID, PAT resolution rules, and local runner notes.
