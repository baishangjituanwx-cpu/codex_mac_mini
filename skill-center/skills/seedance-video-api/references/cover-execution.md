# Cover Execution Scaffold

Use the bundled helper script when the video is already finished and the next task is to lock a repeatable cover package brief before designing or exporting the actual images.

## Script

- `scripts/init_cover_package.py`
- `scripts/extract_cover_candidates.py`
- `scripts/render_cover_package.py`
- `scripts/build_cover_package.py`
- `scripts/init_cover_package.ps1`
- `scripts/extract_cover_candidates.ps1`
- `scripts/render_cover_package.ps1`
- `scripts/build_cover_package.ps1`

For 大陈 / AI员工 Seedance content packages, the canonical renderer is the migration-pack script when the SMB package is mounted:

- `smb://BSJT168._smb._tcp.local/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428/project/scripts/generate_simple_video_covers.py`
- mounted local path usually: `/Volumes/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428/project/scripts/generate_simple_video_covers.py`
- if that path is unavailable, reproduce the same visual style exactly: lower-middle rounded dark translucent card, gold/white dimensional main title, one subtitle line
- do not use a plain full-width bottom strip or platform auto cover as a substitute

## What It Creates

The script creates:

- `cover-brief.md`
- `cover-manifest.json`

inside a chosen output directory, and reserves the standard target filenames:

- `cover-vertical-3x4.png`
- `cover-horizontal-4x3.png`

The candidate-frame script creates:

- `cover-candidates/`
- `cover-candidates.json`
- `cover-contact-sheet.jpg`

The render script creates:

- `cover-vertical-3x4.png`
- `cover-horizontal-4x3.png`

Runtime note:

- `render_cover_package.py` uses Pillow for crop, lower-third overlay, and Chinese text rendering.
- The renderer will auto-detect common macOS and Windows Chinese fonts when `--font-file` is not passed.

## Recommended Usage

macOS / Linux:

```bash
python3 "/Volumes/BSJT 共享给我/AI专用/[Codex]Mac部署/视频制作/大陈AI短视频生产迁移包-20260428/project/scripts/generate_simple_video_covers.py" \
  --frame /absolute/path/to/clean-cover-frame.png \
  --out-dir /absolute/path/to/cover-package \
  --title 'AI员工上岗了' \
  --subtitle '自动跑平台'

python3 /Users/name/.codex/skills/seedance-video-api/scripts/build_cover_package.py \
  --video /absolute/path/to/final_video.mp4 \
  --output-dir /absolute/path/to/cover-package \
  --main-title 'AI员工上岗了' \
  --subtitle '自动跑平台' \
  --candidate-index 2 \
  --tag '平台执行'
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/build_cover_package.ps1 --video C:/work/final_video.mp4 --output-dir C:/work/cover-package --main-title 'AI员工上岗了' --subtitle '自动跑平台' --candidate-index 2 --tag '平台执行'
```

Stage-by-stage flow:

```bash
python3 /Users/name/.codex/skills/seedance-video-api/scripts/init_cover_package.py --video /absolute/path/to/final_video.mp4 --output-dir /absolute/path/to/cover-package --main-title 'AI员工上岗了' --subtitle '自动跑平台' --angle '平台执行类'
python3 /Users/name/.codex/skills/seedance-video-api/scripts/extract_cover_candidates.py --video /absolute/path/to/final_video.mp4 --output-dir /absolute/path/to/cover-package --count 6
python3 /Users/name/.codex/skills/seedance-video-api/scripts/render_cover_package.py --package-dir /absolute/path/to/cover-package --candidate-index 2 --tag '平台执行'
```

```powershell
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/init_cover_package.ps1 --video C:/work/final_video.mp4 --output-dir C:/work/cover-package --main-title 'AI员工上岗了' --subtitle '自动跑平台' --angle '平台执行类'
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/extract_cover_candidates.ps1 --video C:/work/final_video.mp4 --output-dir C:/work/cover-package --count 6
powershell -ExecutionPolicy Bypass -File C:/Users/name/.codex/skills/seedance-video-api/scripts/render_cover_package.ps1 --package-dir C:/work/cover-package --candidate-index 2 --tag '平台执行'
```

## When To Run It

Run it immediately after:

1. the final Seedance video has been downloaded
2. the main title and subtitle direction are known
3. the task is about to move into cover production or platform publishing
4. you want a fast shortlist of still frames before manually designing the final covers

Then run the render script when:

1. the shortlist is ready
2. one candidate frame has been chosen
3. the final PNG covers should be output directly

## Why It Helps

- keeps naming stable across runs
- keeps `3:4` and `4:3` deliverables mandatory
- keeps cover copy and source-video linkage explicit
- makes it easier to hand the cover task to another operator, account, or later automation step
- gives a quick contact sheet and timestamped candidate-frame shortlist for cover selection
- outputs final delivery PNG files from the chosen frame
