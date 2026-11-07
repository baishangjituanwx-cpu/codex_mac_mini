---
name: bysl-image-generation
description: Generate and manage images, videos, and text-to-speech audio through the BYSL (白蚁算力/百亿算力) signed HTTP APIs with the bundled CLI. Use for BYSL setup and diagnostics, Nano or Image-2 generation, AI video generation, 文生视频, 图生视频, Seedance, Wan, Vidu, Veo, Grok or HappyHorse jobs, TTS/语音合成/音色选择, UTF-8 Chinese prompts or narration, reference-image uploads, live model or voice discovery, task polling, result downloads, and NANO_TOKEN-based cross-device deployment.
---

# BYSL Image, Video, and Audio Generation

## Non-negotiable rules

- Use this skill's bundled CLI for every BYSL request.
- Do not reimplement signing or manually craft BYSL HTTP requests.
- Never print, paste, write, commit, summarize, or screenshot `NANO_TOKEN`.
- Put Chinese prompts in a UTF-8 file and pass `--prompt-file`.
- Put Chinese TTS text in a UTF-8 file and pass `--text-file`.
- Do not pipe Chinese JavaScript or JSON through Windows PowerShell stdin.
- Require Node.js 20 or newer.

## Run the CLI

Run from this skill folder or use absolute paths:

```bash
node scripts/bysl-api.js doctor
node scripts/bysl-api.js help
```

On Windows, use the bundled PowerShell wrapper when convenient:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/bysl-image-generation/scripts/bysl-api.ps1 doctor
```

If PowerShell script execution is restricted, fall back to the bundled `cmd` wrapper:

```cmd
C:\Users\name\.codex\skills\bysl-image-generation\scripts\bysl-api.cmd doctor
```

When invoking this skill from Windows, keep local file paths quoted and prefer `C:/Users/<name>/...` style absolute paths for `--prompt-file` and `--out`.

## Authenticate safely

Require `NANO_TOKEN` for authenticated requests. If it is missing, ask the user to log in to `http://bysl.baiyimiandan.com/creative-tools/nano-image` and copy it from the browser console:

```js
copy(JSON.parse(localStorage.getItem('user') || '{}').token)
```

Use the token only through a local environment variable or credential store. Do not write it into the skill or a prompt file.

### macOS persistent credential

Prefer macOS Keychain over writing the token into `.zshrc`. The bundled CLI automatically reads the following Keychain item when `NANO_TOKEN` is not already set:

```text
service: com.bysl.nano-token
account: bysl-nano-token
```

Store or update the item without printing the token. Obtain it through the documented logged-in browser flow, copy it to the clipboard without returning its value to the agent, write it directly to Keychain, then clear temporary shell variables. Never include the value in command text, logs, summaries, screenshots, or ordinary files.

After the browser copy succeeds, update Keychain with the bundled command:

```bash
node scripts/bysl-api.js token-store-clipboard
```

The command validates the clipboard format, stores it in Keychain, clears its in-process variable, and reports only storage status and Keychain identifiers.

When a BYSL request explicitly reports invalid or expired authentication, refresh at most once:

1. Use the logged-in Chrome DevTools MCP page for `bysl.baiyimiandan.com`.
2. Execute the documented `localStorage.user.token` copy operation so the tool returns only success/failure, never the token.
3. Run `node scripts/bysl-api.js token-store-clipboard` to update the same Keychain item without displaying the clipboard.
4. Run `doctor` again and retry the original request only after `api: "ok"`.
5. If the browser is no longer logged in, stop and ask the user to log in; do not inspect cookies or request credentials in chat.

### Windows credential flow

`token-store-clipboard` and automatic Keychain lookup are macOS-only. On Windows, refresh the token from the logged-in browser and keep it in `NANO_TOKEN` without echoing the value in chat, logs, or screenshots.

Recommended refresh flow on Windows:

1. Open the logged-in BYSL page in Chrome and use `Control+Shift+J` or `F12` to focus the DevTools Console.
2. Run `copy(JSON.parse(localStorage.getItem('user') || '{}').token)` in the console.
3. In PowerShell, import the clipboard value directly into the session environment variable, clear the clipboard, and rerun `doctor`:

```powershell
$env:NANO_TOKEN = Get-Clipboard
Set-Clipboard -Value ""
.\scripts\bysl-api.ps1 doctor
```

4. If a dedicated Windows workstation needs a longer-lived user variable, use `setx NANO_TOKEN "REPLACE_WITH_TOKEN"`, close the shell, open a new shell, then rerun `.\scripts\bysl-api.ps1 doctor`. Avoid `setx` on shared machines.

macOS / Linux:

```bash
export NANO_TOKEN="REPLACE_WITH_TOKEN"
node scripts/bysl-api.js doctor
```

Windows PowerShell:

```powershell
$env:NANO_TOKEN="REPLACE_WITH_TOKEN"
.\scripts\bysl-api.ps1 doctor
```

Run `doctor` before the first live job. Continue only when it reports `api: "ok"`.

## Handle prompts and references

Write Chinese prompts as UTF-8 and pass their path with `--prompt-file`. On Windows, use `Set-Content -Encoding utf8` or an editor that preserves UTF-8.

Upload every local reference image before a BYSL job:

```bash
node scripts/bysl-api.js upload refs/product.png
```

Read the returned HTTP(S)/OSS URL from the command's JSON response and use it with `--images`. The response field name can vary, so do not hard-code a field path without inspecting the actual response. Do not pass a local path to `--images`, `--first-frame`, or `--last-frame`.

## Generate images

Image-2:

```bash
node scripts/bysl-api.js image-create --model-id 63 --ratio 9:16 --prompt-file prompt.md --out outputs/image2.png
```

Nano:

```bash
node scripts/bysl-api.js nano-create --ratio 1:1 --prompt-file prompt.md --out outputs/nano.png
```

Inspect models and history without creating a task:

```bash
node scripts/bysl-api.js image-model-groups
node scripts/bysl-api.js image-models
node scripts/bysl-api.js list --type image --page 1 --pagesize 10
node scripts/bysl-api.js list --type nano --page 1 --pagesize 10
```

## Generate videos

Query the live model list before selecting a model when model availability may have changed:

```bash
node scripts/bysl-api.js video-model-groups
node scripts/bysl-api.js video-models
node scripts/bysl-api.js video-category
```

Create a text-to-video job:

```bash
node scripts/bysl-api.js video-create --model-id 71 --prompt-file prompt.md --ratio 16:9 --duration 5 --resolution 720 --out outputs/video.mp4
```

Create an image-to-video job after uploading the reference image:

```bash
node scripts/bysl-api.js video-create --model-id 72 --prompt-file prompt.md --images "https://example.com/ref.png" --duration 5 --resolution 720 --out outputs/video.mp4
```

For Seedance, use `--model-type 1` with `--first-frame` and optional `--last-frame`. Use `--model-type 2` with `--images` for multimodal reference-image mode, subject to the live model's supported options.

Seedance first/last-frame example:

```bash
node scripts/bysl-api.js video-create --model-id 47 --prompt-file prompt.md --model-type 1 --first-frame "https://example.com/first.png" --last-frame "https://example.com/last.png" --ratio 16:9 --duration 5 --out outputs/video.mp4
```

Inspect video history without creating a task:

```bash
node scripts/bysl-api.js video-list --page 1 --pagesize 10
```

Video jobs can take 30 seconds to 5 minutes. The CLI defaults to 120 polls at 10-second intervals. Increase polling only when the upstream queue remains active:

```bash
node scripts/bysl-api.js video-create --model-id 72 --prompt-file prompt.md --images "https://example.com/ref.png" --max-polls 180 --interval-ms 10000 --out outputs/video.mp4
```

Windows PowerShell example with quoted local paths:

```powershell
.\scripts\bysl-api.ps1 video-create --model-id 71 --prompt-file "C:/Users/name/Documents/bysl/prompt.md" --ratio 16:9 --duration 5 --resolution 720 --out "C:/Users/name/Documents/bysl/video.mp4"
```

Read [references/video.md](references/video.md) when selecting a video model or validating model-specific parameters.

### Product-advertising preservation

- Query the live model ID, supported parameters, and account credit before every paid-advertising generation batch.
- For packaging, labels, fixed quantities, colors, or fine product structures, generate only a product-free, brand-free, text-free background. Composite verified real product pixels locally and deterministically after video generation.
- Never approve a result where the model redraws packaging text, changes quantity/color, or deforms the product. Check every second, every scene cut, and the tail frame.
- Before upload, also verify container/codecs, DAR/SAR, full decode, black/frozen frames, A/V timing, subtitles, loudness, clipping, and a full human listening pass when audio is present.
- Distinguish machine QA from user listening acceptance; do not silently convert `HUMAN_AUDIO_REVIEW_REQUIRED` into a machine pass.

## Generate text-to-speech audio

Query live voice data before selecting a voice ID:

```bash
node scripts/bysl-api.js tts-voice-categories
node scripts/bysl-api.js tts-voices --type 0 --cate-id 48 --page 1 --pagesize 20 --status 3
node scripts/bysl-api.js tts-history --page 1 --pagesize 10
```

Write the narration as UTF-8 and download the generated audio directly:

```bash
node scripts/bysl-api.js tts-create --voice-id 128 --text-file narration.txt --volume 1 --rate 1 --pitch 1 --out outputs/narration.wav
```

Windows PowerShell example with quoted UTF-8 paths:

```powershell
Set-Content -Path "C:/Users/name/Documents/bysl/narration.txt" -Value "这里写中文旁白" -Encoding utf8
.\scripts\bysl-api.ps1 tts-create --voice-id 128 --text-file "C:/Users/name/Documents/bysl/narration.txt" --volume 1 --rate 1 --pitch 1 --out "C:/Users/name/Documents/bysl/narration.wav"
```

Use a `voice_id` from the live list; do not assume a documented ID is still available. The web UI exposes volume `0–1`, rate `0.5–2`, and pitch `0.5–2`, all with defaults of `1`. The synthesis response is synchronous. The CLI downloads the returned audio URL when `--out` is supplied and omits that URL from stdout.

After generation, decode-probe and listen to the complete file. Record the detected codec/container, duration, sample rate, channels, and bitrate. Do not infer the actual format only from the chosen filename extension.

Read [references/audio.md](references/audio.md) for TTS endpoints, flags, validation, and safety details.

## Verify every generation

- Confirm `diagnostics.questionMarkCount` is `0` unless the prompt intentionally contains `?`.
- Confirm the task reached status `5`; treat status `6` as failed.
- Confirm the output file exists and has non-zero bytes.
- For TTS, confirm the audio decodes and manually review the full spoken content before publishing.
- Prefer `video_url_clean` for video downloads when the API provides it.
- Treat long pending or processing states as upstream queueing; retry with longer polling instead of rewriting the API call.
- Report the output path and task status without exposing credentials.

## Load API details only when needed

Read [references/api.md](references/api.md) only when endpoint fields, payload shapes, status codes, signing context, or request debugging details are needed.
