# Runtime Config

## Live Runtime Target

Current configured workflow target:

- workflow id: `7626331907709812776`
- base URL: `https://api.coze.cn`

Runtime config file:

- [config.json](/Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/config.json)

## PAT Resolution Order

The local runner resolves the PAT in this order:

1. environment variable `COZE_PAT`
2. macOS Keychain service `codex.coze-seedance15pro-sales-workflow.pat`

The preferred long-term setup is Keychain storage, not a plaintext token in skill docs.

## Local Runner

Runner path:

- [run_workflow.py](/Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/scripts/run_workflow.py)

## Two Explicit Modes

### 文生视频

Required:

- `prompt`

Typical payload:

```json
{
  "prompt": "一只可爱的小猫在草地上玩耍",
  "duration": 5,
  "ratio": "16:9",
  "resolution": "720p",
  "generate_audio": true
}
```

### 图生视频

Required:

- `prompt`
- `image_url`

Typical payload:

```json
{
  "prompt": "人物缓缓转头微笑",
  "image_url": "https://example.com/first-frame.jpg",
  "duration": 5,
  "ratio": "9:16",
  "resolution": "720p",
  "generate_audio": true
}
```

Supported CLI parameters:

- `--prompt`
- `--image-url`
- `--bot-id`
- `--duration`
- `--ratio`
- `--resolution`
- `--generate-audio`
- `--async`
- `--poll-interval`
- `--max-wait`
- `--request-timeout`
- `--output-dir`
- `--skip-download`
- `--print-config`

## Execution Standard Alignment

The local runner now matches the official Coze workflow-run contract more closely:

- sync run: `workflow_id` + `parameters`
- optional `bot_id`
- optional `is_async: true`
- async history polling through `/v1/workflows/{workflow_id}/run_histories/{execute_id}`

For long-running video jobs, async mode is usually safer than waiting for one long synchronous HTTP response.

## Important Distinction

- [references/exported-workflow.yaml](/Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/references/exported-workflow.yaml) is the archived export that originally seeded this skill.
- [config.json](/Users/baishangjituan/.codex/skills/coze-seedance15pro-sales-workflow/config.json) is the current live runtime configuration.

Do not assume the archived export ID must always equal the live runtime workflow ID.
