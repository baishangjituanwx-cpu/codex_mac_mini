# BYSL API Reference

Base URL: `http://bysl.baiyimiandan.com`

Auth token source: `localStorage.user.token` on the logged-in BYSL page.

Signing formula:

```text
md5(cloudid + sign_key + pathname.toLowerCase() + time + "pc1" + token + custom)
```

Common endpoints:

```text
POST /api/common/base
POST /api/user/info
POST /api/common/upload
POST /api/ai_image/list
POST /api/ai_image/nano_banana
POST /api/ai_image/image_model_type
POST /api/ai_video/video_model
POST /api/ai_image/image_create
```

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

Task status values observed:

```text
1 pending
3 processing
5 completed
6 failed
```

For Image-2 history, call `/api/ai_image/list` with:

```json
{ "page": 1, "pagesize": 10, "type": 2 }
```

For Nano history, call `/api/ai_image/list` without `type`.
