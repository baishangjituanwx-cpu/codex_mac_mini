# BYSL Text-to-Speech

Use this reference for BYSL text-to-speech jobs. The implementation mirrors the live 2026-08-10 web client at `/creative-tools/text-to-speech`.

## Read-only discovery

```bash
node scripts/bysl-api.js doctor
node scripts/bysl-api.js tts-voice-categories
node scripts/bysl-api.js tts-voices --type 0 --cate-id 48 --page 1 --pagesize 20 --status 3
node scripts/bysl-api.js tts-voices --type 1 --page 1 --pagesize 20 --status 3
node scripts/bysl-api.js tts-history --page 1 --pagesize 10
```

Use the live voice list to select a positive integer `voice_id`. Do not guess an ID from documentation snapshots.

## Generate audio

Write narration text as UTF-8, then generate and download in one command:

```bash
node scripts/bysl-api.js tts-create \
  --voice-id 128 \
  --text-file narration.txt \
  --volume 1 \
  --rate 1 \
  --pitch 1 \
  --out outputs/narration.wav
```

Windows PowerShell equivalent:

```powershell
Set-Content -Path "C:/Users/name/Documents/bysl/narration.txt" -Value "这里写中文旁白" -Encoding utf8
.\scripts\bysl-api.ps1 tts-create --voice-id 128 --text-file "C:/Users/name/Documents/bysl/narration.txt" --volume 1 --rate 1 --pitch 1 --out "C:/Users/name/Documents/bysl/narration.wav"
```

If PowerShell execution policy blocks the wrapper, run the same arguments through `scripts\\bysl-api.cmd`. Keep Windows local paths quoted and prefer `C:/Users/<name>/...` form.

The live page exposes these ranges:

| Flag | Default | Range | Step in web UI |
|---|---:|---:|---:|
| `--volume` | 1 | 0–1 | 0.1 |
| `--rate` | 1 | 0.5–2 | 0.1 |
| `--pitch` | 1 | 0.5–2 | 0.1 |

The web client sends `voice_id`, `text`, `volume`, `pitch`, and `rate` to `POST /api/audio/synthesis`. It receives an audio URL synchronously. The CLI downloads the result when `--out` is present and deliberately omits the URL from stdout.

If Node's bundled CA set cannot validate the OSS certificate chain, the client retries the result download with the operating system's `curl` certificate store. It never disables TLS verification.

## Validate output

- Confirm the output exists and has non-zero bytes.
- Use `ffprobe` or another decoder to confirm the file is readable and record the actual codec, container, duration, sample rate, channel count, and bitrate.
- Listen to the entire file before publishing. Check pronunciation, missing or duplicated words, clipping, silence, and unintended content.
- Treat the filename extension suggested by the web page as a convenience only; trust the downloaded file's detected container and codec.
- Do not store `NANO_TOKEN`, cookies, request signatures, or returned audio URLs in manifests or reports.
