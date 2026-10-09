# BYSL Video Models and Parameters

Use this reference only for video jobs. Query `video-models` before a live job because server-side availability can change.

For commercial product footage, do not send label-sensitive product pixels to a
generative video model when exact packaging, quantity, color, or structure must stay
unchanged. Prefer a generated empty background plus deterministic local foreground
composition, then inspect every second, all cuts, and the final frame. Use only
durations and resolutions returned by the live model schema; never fix them from an
old example.

## Parameters

| CLI flag | Required | Meaning |
|---|---:|---|
| `--model-id` | Yes | Positive integer model ID |
| `--prompt-file` | Yes | UTF-8 prompt file |
| `--ratio` | Model-dependent | `16:9`, `9:16`, `1:1`, or `adaptive` |
| `--duration` | Model-dependent | Common values: `5`, `6`, `8`, `10`, `15` seconds |
| `--resolution` | Model-dependent | Common values: `480`, `540`, `720`, `1080`, `4` |
| `--images` | Image-to-video | One or more uploaded image URLs, comma-separated |
| `--model-type` | Seedance | Use `1` with `--first-frame`/`--last-frame`; use `2` with multimodal `--images` references |
| `--first-frame` | Seedance | Uploaded first-frame URL |
| `--last-frame` | Seedance | Optional uploaded last-frame URL |
| `--prompt-extend` | Wan | Enable or disable prompt rewriting |
| `--out` | No | Download path for the completed video |
| `--max-polls` | No | Poll limit; default `120` for video |
| `--interval-ms` | No | Poll interval; default `10000` ms for video |

## Model snapshot

This is the 2026-08-04 documentation snapshot. Prefer the live `video-models` response when it differs.

### Image-to-video

| ID | Model | Provider | Reference limit |
|---:|---|---|---:|
| 72 | Wan 2.7 图生视频 | 万象 | 2 |
| 68 | Viduq3 Turbo 图生视频 | 生数 | 2 |
| 67 | Viduq3 Pro 图生视频 | 生数 | 2 |
| 47 | Seedance 2.0 图生视频 | 字节 | 9 |
| 48 | Seedance 2.0 图生视频 极速版 | 字节 | 9 |
| 104 | Seedance 2.0 mini 图生视频 | 字节 | 9 |
| 7 | Wan 2.6 图生视频 极速版 | 万象 | 1 |
| 75 | Happyhorse 1.0 参考生视频 | HappyHorse | 9 |
| 74 | Happyhorse 1.0 图生视频 | HappyHorse | 1 |
| 9 | Grok Imagine 高性价比 | xAI | 2 |

### Text-to-video

| ID | Model | Provider |
|---:|---|---|
| 71 | Wan 2.7 文生视频 | 万象 |
| 70 | Viduq3 Turbo 文生视频 | 生数 |
| 69 | Viduq3 Pro 文生视频 | 生数 |
| 49 | Seedance 2.0 文生视频 | 字节 |
| 50 | Seedance 2.0 文生视频 极速版 | 字节 |
| 103 | Seedance 2.0 mini 文生视频 | 字节 |
| 73 | Happyhorse 1.0 文生视频 | HappyHorse |
| 6 | Wan 2.6 文生视频 标准版 | 万象 |

### Special

| ID | Model | Provider | Notes |
|---:|---|---|---|
| 11 | Veo3.1 专业版 | Google | 8 seconds, up to 4K, optional references |
