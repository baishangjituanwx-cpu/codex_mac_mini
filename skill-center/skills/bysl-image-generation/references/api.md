# BYSL API Reference

Base URL: `http://bysl.baiyimiandan.com`

Auth token source: `localStorage.user.token` on the logged-in BYSL page.

The bundled CLI implements the observed signature formula:

```text
md5(cloudid + sign_key + pathname.toLowerCase() + time + "pc1" + token + custom)
```

Do not reproduce this logic outside the bundled client.

## Endpoints

Common and image endpoints:

```text
POST /api/common/base
POST /api/user/info
POST /api/common/upload
POST /api/ai_image/list
POST /api/ai_image/nano_banana
POST /api/ai_image/image_model_type
POST /api/ai_image/image_create
```

Video endpoints:

```text
POST /api/ai_video/video_model
POST /api/ai_video/video_create
POST /api/ai_video/list
POST /api/ai_video/video_model_type
POST /api/ai_video/category
```

## Payloads

Image-2:

```json
{
  "model_id": 63,
  "prompt": "UTF-8 prompt text",
  "image": "https://example.com/ref1.png,https://example.com/ref2.png",
  "ratio": "9:16"
}
```

Nano:

```json
{
  "content": "UTF-8 prompt text",
  "is_pro": true,
  "ratio": "1:1",
  "images": "https://example.com/ref.png",
  "resolution_s": "1K"
}
```

Video:

```json
{
  "model_id": 72,
  "prompt": "UTF-8 prompt text",
  "image": "https://example.com/ref.png",
  "ratio": "16:9",
  "duration": 5,
  "resolution": 720
}
```

Seedance first/last-frame mode can additionally send `model_type`, `first_frame`, and `last_frame`. Wan models can send `prompt_extend`.

## Task states

```text
1 pending
3 processing
5 completed
6 failed
```

For Image-2 history, call `/api/ai_image/list` with `type: 2`. For Nano history, omit `type`. Video history comes from `/api/ai_video/list`; completed items may contain `video_url` and `video_url_clean`, where `video_url_clean` is the no-watermark result.
