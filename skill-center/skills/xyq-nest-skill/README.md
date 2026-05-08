# 🎬 xyq-nest-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../../LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)

## 🚀 简介

`xyq-nest-skill` 通过接入小云雀NestAgent的综合创作能力，实现AI图片/视频的生成、编辑、风格转换等功能。

## 🧰 环境与平台

必填环境变量：

```bash
export XYQ_ACCESS_KEY="your-access-key"
```

Windows PowerShell 等价写法：

```powershell
$env:XYQ_ACCESS_KEY = "your-access-key"
```

Windows 仓库镜像同时提供 PowerShell 包装器：

- `scripts/submit_run.ps1`
- `scripts/get_thread.ps1`
- `scripts/upload_file.ps1`
- `scripts/download_results.ps1`
- 对应的 `.cmd` 包装器

这些 `.ps1` 文件会自动寻找 `.venv\Scripts\python.exe`、激活中的虚拟环境，或系统里的 `py` / `python` / `python3`，避免把 Windows 流程写死成 `python3`.

Windows 路径规则：

- 本地素材路径一律用带引号的绝对路径，例如 `C:/Users/alice/Downloads/ref.png`
- `--output-dir` 也用 quoted `C:/...` 绝对路径，避免混用 `/Users/...`、反斜杠转义或未加引号的含空格路径

## ✨ 功能特性

| 功能 | 说明                               |
|------|----------------------------------|
| 📨 创建会话 / 发送消息 | 向小云雀发送自然语言指令，生成图片或视频             |
| 🔍 查询会话进展 | 增量拉取会话消息，轮询创作进度和产物结果             |
| 📤 上传文件 | 上传图片/视频到小云雀资产库，获取 `资产ID` 用于编辑和参考 |
| 📥 下载结果 | 批量下载生成的图片/视频到本地，支持并行下载           |

**🎨 小云雀平台能力覆盖：**

- **生成**：文生图、文生视频、图生视频、视频续写
- **编辑**：局部修改、元素替换、镜头调整、风格迁移
- **复杂创作**：一句话生成短剧（剧本→分镜→成片）、复刻视频/TVC/宣传片、音乐 MV 生成、产品展示片制作

### 📨 创建会话 / 发送消息

```bash
# 创建新会话
python3 skills/xyq-nest-skill/scripts/submit_run.py --message "生一个动漫视频"

# 向已有会话发送消息
python3 skills/xyq-nest-skill/scripts/submit_run.py --message "再生成一个故事视频" --thread-id THREAD_ID

# 携带参考文件发送
python3 skills/xyq-nest-skill/scripts/submit_run.py --message "参考这个视频做修改" --asset-ids asset_id1 asset_id2
```

Windows PowerShell equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\submit_run.ps1 --message "生一个动漫视频"
.\skill-center\skills\xyq-nest-skill\scripts\submit_run.ps1 --message "再生成一个故事视频" --thread-id THREAD_ID
.\skill-center\skills\xyq-nest-skill\scripts\submit_run.ps1 --message "参考这个视频做修改" --asset-ids asset_id1 asset_id2
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--message` | 是 | 创作指令内容 |
| `--thread-id` | 否 | 已有会话 ID，不传则创建新会话 |
| `--asset-ids` | 否 | 资产 ID 列表，支持多个 |

**返回：**

```json
{
  "thread_id": "90f05e0c-...",
  "run_id": "abc123-..."
}
```

### 🔍 查询会话进展

```bash
python3 skills/xyq-nest-skill/scripts/get_thread.py --thread-id THREAD_ID --run-id RUN_ID --after-seq 0
```

Windows PowerShell equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\get_thread.ps1 --thread-id THREAD_ID --run-id RUN_ID --after-seq 0
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--thread-id` | 是 | 会话 ID |
| `--run-id` | 否 | 运行 ID |
| `--after-seq` | 否 | 增量拉取起始序号，默认 0 |

**返回：**

```json
{
  "messages": [
    {"id": "1", "role": "user", "content": "生一个动漫视频"},
    {"id": "2", "role": "assistant", "content": [{"type": "...", "subtype": "...", "data": {...}}]},
    {"id": "3", "role": "assistant", "content": [{"type": "...", "data": {"url": "https://..."}}]}
  ]
}
```

### 📤 上传文件

```bash
# 上传图片
python3 skills/xyq-nest-skill/scripts/upload_file.py /path/to/image.png

# 上传视频
python3 skills/xyq-nest-skill/scripts/upload_file.py /path/to/video.mp4
```

Windows PowerShell equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\upload_file.ps1 "C:/Users/alice/Downloads/image.png"
.\skill-center\skills\xyq-nest-skill\scripts\upload_file.ps1 "C:/Users/alice/Videos/video.mp4"
```

仅支持 `image/*` 和 `video/*` 类型，单文件大小限制 200MB。

**返回：**

```json
{
  "asset_id": "asset_xxx"
}
```

### 📥 下载结果

```bash
python3 skills/xyq-nest-skill/scripts/download_results.py \
  --urls URL1 URL2 URL3 \
  --output-dir ./xyq_output \
  --prefix "storyboard" \
  --workers 5
```

Windows PowerShell equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\download_results.ps1 `
  --urls URL1 URL2 URL3 `
  --output-dir "C:/Users/alice/Downloads/xyq_output" `
  --prefix "storyboard" `
  --workers 5
```

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--urls` | 是 | 要下载的 URL 列表 |
| `--output-dir` | 否 | 输出目录，默认 `./xyq_output` |
| `--prefix` | 否 | 文件名前缀，如 `storyboard` → `storyboard_01.png` |
| `--workers` | 否 | 并行下载线程数，默认 5 |

**返回：**

```json
{
  "output_dir": "./xyq_output",
  "downloaded": ["./xyq_output/storyboard_01.png", "..."],
  "total": 3
}
```

## 🎯 典型示例

### 🎬 文生视频（最常见）

```
1. submit_run.py --message "生成一个赛博朋克风格的城市夜景视频"
   → 拿到 thread_id、run_id

2. 每 10 秒轮询：
   get_thread.py --thread-id THREAD_ID --run-id RUN_ID --after-seq SEQUENCE
   → ⏳ 进行中：展示创作信息，继续轮询
   → ❓ 意图确认：展示问题，等用户回复后用同一 thread_id 重新提交
   → ✅ 完成：提取产物 URL，下载并展示结果

3. download_results.py --urls URL1 URL2 --output-dir ./output --prefix "cyberpunk"
```

### ✂️ 编辑已有视频

```
1. upload_file.py /path/to/video.mp4
   → 拿到 asset_id

2. submit_run.py --message "把背景换成星空" --asset-ids asset_id

3. 同场景 1 的轮询和下载流程
```

### 🖼️ 多参考图生成

```
1. upload_file.py /path/to/ref1.png → asset_id1
2. upload_file.py /path/to/ref2.png → asset_id2
3. upload_file.py /path/to/ref3.mp4 → asset_id3
   （多文件可并行上传）

4. submit_run.py --message "根据参考图和视频生成科普故事视频" --asset-ids asset_id1 asset_id2 asset_id3

5. 同场景 1 的轮询和下载流程
```

### 💬 在已有会话中追加需求

```
1. submit_run.py --message "把刚才的视频加个片头" --thread-id EXISTING_THREAD_ID
   → 新的 run_id

2. 同场景 1 的轮询和下载流程
```

### ⏱️ 轮询策略

- **间隔**：每 10 秒查询一次
- **增量拉取**：首次 `--after-seq 0`，后续根据已获取消息数计算新 seq
- **超时**：连续轮询 48 小时无结果则停止
- **错误重试**：单次失败可重试 1 次，连续 3 次失败则停止

## 🪟 Windows 速记

- 运行命令优先用仓库里的 `.ps1` 包装器，不要假定 Windows 一定存在 `python3`.
- 素材和输出目录都用 quoted `C:/...` 绝对路径。
- 如果路径里包含空格，PowerShell 命令参数必须整体加引号。
- API 逻辑仍然是同一套 Python 脚本，Windows 只是补齐执行入口和路径写法，不做行为分叉。
