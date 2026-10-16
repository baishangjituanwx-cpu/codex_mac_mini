# Seedance API Basics

## Endpoints

- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- Create task: `POST /contents/generations/tasks`
- Query task: `GET /contents/generations/tasks/{id}`

## Authentication

- Use `Authorization: Bearer $ARK_API_KEY`
- Keep the key outside tracked files
- Prefer environment variables over command-line secret passing

## Model IDs

- `Seedance 2.0`: `doubao-seedance-2-0-260128`
- `Seedance 2.0 Fast`: `doubao-seedance-2-0-fast-260128`

## Output Limits

- Output duration: `4-15s`
- `duration=-1` is allowed, but still within the supported model range
- Supported output resolutions for 2.0 / Fast: `480p`, `720p`
- `1080p` is not supported for 2.0 / Fast

## Input Content Types

- `text`
- `image_url`
- `video_url`
- `audio_url`
- `draft_task`

## Role Notes

- `video_url.role`: currently `reference_video`
- `audio_url.role`: currently `reference_audio`
- Single image without role usually maps to `first_frame`
- Multiple images without roles usually map to `reference_image`

## Media Constraints

- Single reference video duration: `[2, 15]s`
- Up to `3` reference videos
- Total input reference-video duration must not exceed `15s`
- Local video files are not valid for `video_url.url`; use public URLs or `asset://...`
- Audio cannot be sent alone; pair it with at least one image or video reference

## Task Lifetime

- Result `video_url` is cleaned after about `24h`
- `last_frame_url` is also temporary
- Query records are only retained for a limited recent window

## Extension Implication

Because output is capped at `15s` and total input reference-video duration is also capped at `15s`, `30s+` outputs must be built across multiple tasks and stitched later.
