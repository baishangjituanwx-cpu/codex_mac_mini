---
name: bysl-image-generation
description: Use when generating or managing images through bysl.baiyimiandan.com Nano or Image-2 APIs, including agent automation, UTF-8 Chinese prompts, task polling, downloads, uploads, and token-based setup. Use for BYSL, 白蚁算力, Nano 生图, Image-2 生图, and Codex image generation workflows that should call BYSL instead of reimplementing API requests.
---

# BYSL Image Generation

## Required Rule

Use this skill's bundled CLI. Do not reimplement HTTP signing or manually craft BYSL requests.

Run commands from this skill folder unless an absolute path is easier:

```bash
cd ~/.codex/skills/bysl-image-generation
node scripts/bysl-api.js doctor
```

If the skill mirror is synced onto a Windows machine, prefer the PowerShell wrapper instead of invoking the JS file through stdin:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/bysl-image-generation/scripts/bysl-api.ps1 doctor
```

## Token

`NANO_TOKEN` is required for authenticated requests. Never print, paste, write, or commit the token.

Get it from the logged-in BYSL web page console:

```js
copy(JSON.parse(localStorage.getItem('user') || '{}').token)
```

Use it only as an environment variable:

```bash
NANO_TOKEN="REPLACE_WITH_TOKEN" node scripts/bysl-api.js doctor
```

Windows PowerShell equivalent:

```powershell
$env:NANO_TOKEN = "REPLACE_WITH_TOKEN"
.\scripts\bysl-api.ps1 doctor
```

## Prompt Handling

For Chinese prompts, always write a UTF-8 prompt file and pass `--prompt-file`.

Do not pipe Chinese JavaScript or JSON through Windows PowerShell stdin; that path previously converted Chinese text into `?`.

macOS / generic example:

```bash
cat > prompt.md <<'EOF'
中文提示词
EOF
```

Windows PowerShell-safe example:

```powershell
@'
中文提示词
'@ | Set-Content -Path .\prompt.md -Encoding utf8
```

## Windows PowerShell Quick Use

Use the bundled PowerShell launcher when the skill mirror is synced onto a Windows machine:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/bysl-image-generation/scripts/bysl-api.ps1 doctor
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/bysl-image-generation/scripts/bysl-api.ps1 image-create --model-id 63 --ratio 9:16 --prompt-file C:/work/prompt.md --out C:/work/outputs/image2.png
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/bysl-image-generation/scripts/bysl-api.ps1 nano-create --ratio 1:1 --prompt-file C:/work/prompt.md --out C:/work/outputs/nano.png
```

Windows path handling rules:

- Prefer quoted absolute paths.
- Prefer `C:/...` forward-slash paths in prompts, output arguments, and copied examples.
- Keep prompt text in UTF-8 files written with `Set-Content -Encoding utf8`, `Out-File -Encoding utf8`, or an editor that saves UTF-8 without re-encoding through stdin.
- The PowerShell wrapper resolves `node` or `node.exe` from `PATH`; if neither exists, install Node.js first instead of rewriting the CLI.

## macOS Quick Use

Use the bundled JS CLI directly on macOS or other shells:

```bash
cd /Users/name/.codex/skills/bysl-image-generation
node scripts/bysl-api.js doctor
node scripts/bysl-api.js image-create --model-id 63 --ratio 9:16 --prompt-file /Users/name/work/prompt.md --out /Users/name/work/outputs/image2.png
node scripts/bysl-api.js nano-create --ratio 1:1 --prompt-file /Users/name/work/prompt.md --out /Users/name/work/outputs/nano.png
```

## Common Commands

Image-2:

```bash
node scripts/bysl-api.js image-create --model-id 63 --ratio 9:16 --prompt-file prompt.md --out outputs/image2.png
```

Nano:

```bash
node scripts/bysl-api.js nano-create --ratio 1:1 --prompt-file prompt.md --out outputs/nano.png
```

Windows PowerShell equivalents:

```powershell
.\scripts\bysl-api.ps1 image-create --model-id 63 --ratio 9:16 --prompt-file .\prompt.md --out .\outputs\image2.png
.\scripts\bysl-api.ps1 nano-create --ratio 1:1 --prompt-file .\prompt.md --out .\outputs\nano.png
```

List tasks:

```bash
node scripts/bysl-api.js list --type image --page 1 --pagesize 10
node scripts/bysl-api.js list --type nano --page 1 --pagesize 10
```

Upload reference images:

```bash
node scripts/bysl-api.js upload refs/product.png
```

Windows wrappers are also available as:

- `scripts/bysl-api.ps1`
- `scripts/bysl-api.cmd`

## Verification

After generation, confirm:

- CLI JSON includes `diagnostics.questionMarkCount: 0` unless the prompt intentionally contains `?`.
- Task reached status `5`.
- Output file exists and has non-zero bytes.
- Do not expose `NANO_TOKEN` in summaries, logs, screenshots, or committed files.

## Details

Read `references/api.md` only when endpoint fields, status codes, or model IDs are needed.
