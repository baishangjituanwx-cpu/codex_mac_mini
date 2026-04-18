---
name: seedance-video-api
description: Use when the user wants to create, inspect, extend, poll, or download Volcengine Ark Seedance 2.0 / 2.0 Fast video tasks through the direct API, including text-to-video, first-frame image-to-video, multimodal reference generation, 15-second extension chaining, and payload preparation with the bundled CLI; requires a locally set `ARK_API_KEY` and must never store or request the full key in chat or tracked files.
---

# Seedance Video API

Direct Volcengine Ark Seedance 2.0 / 2.0 Fast workflows for Codex. Use the bundled CLI and payload templates for safe direct API work instead of re-building requests each time.

## When To Use

- The user wants direct API access to `Seedance 2.0` or `Seedance 2.0 Fast`
- The user wants to submit or poll Ark video-generation tasks
- The user wants payload templates for text-to-video, first-frame image-to-video, multimodal reference video, or extension
- The user wants to build longer videos from chained `4-15s` Seedance segments
- The user wants to download `video_url` or `last_frame_url` from an existing task

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

## Windows PowerShell Quick Use

Use the bundled PowerShell launcher when the skill mirror is synced onto a Windows machine:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.ps1 submit --payload C:/work/payload.json --dry-run
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.ps1 wait cgt-xxxx --download C:/work/output.mp4
```

Windows path handling rules:

- Prefer quoted absolute paths.
- Prefer `C:/...` forward-slash paths in JSON payloads so they also stay valid on macOS hosts.
- The PowerShell launcher will try `.venv\\Scripts\\python.exe`, an active virtualenv, `py -3`, `python`, then an installed `uv` managed Python.

## macOS Quick Use

Use the bundled shell launcher when the skill mirror is synced onto a Mac:

```bash
bash /Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.sh submit --payload /Users/name/work/payload.json --dry-run
bash /Users/name/.codex/skills/seedance-video-api/scripts/seedance_cli.sh wait cgt-xxxx --download /Users/name/work/output.mp4
```

macOS path handling rules:

- Prefer quoted absolute paths.
- Prefer `python3` or a local virtualenv with Python `3.10+`.
- The shell launcher will try `./.venv/bin/python`, an active virtualenv, `python3`, `python`, then an installed `uv` managed Python.

## Bundled CLI

Primary script:

- `scripts/seedance_cli.py`
- `scripts/seedance_cli.sh`
- `scripts/seedance_cli.ps1`

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
