---
platforms:
  - douyin
  - wechat_channels
  - kuaishou
  - weibo
status: ready_for_publish
theme: "{{THEME}}"
video_asset_path: "{{ASSET_ROOT}}/master.mp4"
alternate_video_asset_path: "{{ASSET_ROOT}}/master_alt.mp4"
upload_video_path: "{{ASSET_ROOT}}/publish.mp4"
brief_path: "{{ASSET_ROOT}}/brief.json"
prompt_package_path: "{{ASSET_ROOT}}/video-prompt.txt"
seedance_payload_path: "{{ASSET_ROOT}}/seedance_payload.json"
publish_plan_path: "{{ASSET_ROOT}}/publish-plan.md"
browser_use_checklist_path: "{{ASSET_ROOT}}/browser-use-checklist.md"
final_verify_path: "{{ASSET_ROOT}}/final-verify.json"
cover_vertical_path: "{{ASSET_ROOT}}/covers/cover_vertical_3x4.jpg"
cover_horizontal_path: "{{ASSET_ROOT}}/covers/cover_horizontal_4x3.jpg"
---

# 视频平台发布包

> 这个文件里的字段必须是可直接发布的真实版本。
> `ready_for_publish` 状态下，不允许保留空白标题、空白描述或“后续再写”的占位内容。
> 发布文案必须先读取当前内容线最近一次已完成的数据复盘；没有新复盘时，要明确写明沿用的是哪一份已验证复盘。
> 每个平台都必须显式写出上传视频文件、上传封面文件和要粘贴的标题/文案，不能只给方向。

## 一、主视频

- 原始视频: `{{ASSET_ROOT}}/master.mp4`
- 兼容旧流程备用视频: `{{ASSET_ROOT}}/master_alt.mp4`
- 上传视频: `{{ASSET_ROOT}}/publish.mp4`
- brief: `{{ASSET_ROOT}}/brief.json`
- 复盘依据: `{{ASSET_ROOT}}/latest-review.md`
- 视频提示词: `{{ASSET_ROOT}}/video-prompt.txt`
- 标准化 payload: `{{ASSET_ROOT}}/seedance_payload.json`
- 发布计划: `{{ASSET_ROOT}}/publish-plan.md`
- 浏览器执行清单: `{{ASSET_ROOT}}/browser-use-checklist.md`
- 最终验收记录: `{{ASSET_ROOT}}/final-verify.json`
- 平台上传清单: `{{ASSET_ROOT}}/platform-upload-map.md`

## 二、抖音

### 上传素材

- 上传视频：
- 上传封面 `3:4`：
- 上传封面 `4:3`：

### 标题


### 文案


### 包装自检

- 标题尽量不超过 `20` 个可见中文字符
- 文案首句尽量不超过 `18` 个可见中文字符
- 标题与文案首句不要出现重复的 `3` 个及以上连续字串
- 可用 `node /Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/scripts/douyin-packaging-guard.mjs --brief {{ASSET_ROOT}}/brief.json` 做硬校验
- 最终以 `作品管理` 顶行缩略图和列表文案为准，不以编辑页表单值为准


## 三、快手

### 上传素材

- 上传视频：
- 主用封面 `3:4`：
- 备用封面 `4:3`：

### 标题


### 文案


## 四、视频号

### 上传素材

- 上传视频：
- 主用封面 `3:4`：
- 备用封面 `4:3`：

### 短标题


### 描述


## 五、微博视频版

### 上传素材

- 上传视频：
- 主用封面 `3:4`：
- 备用封面 `4:3`：

### 标题


### 配文


## 六、B站

### 上传素材

- 上传视频：
- 主用封面 `4:3`：
- 备用封面 `3:4`：

### 标题


### 简介


## 六点五、头条号视频版

### 上传素材

- 上传视频：
- 主用封面 `3:4`：
- 备用封面 `4:3`：

### 标题


### 描述


## 七、执行规则

- 标题 / 短标题 / 文案 / 描述不得留空
- 所有字段都必须是可直接粘贴到后台的真实版本
- 标题和描述用真实输入
- 发布前先核对目标账号名和账号 ID
- 发布前先看管理页
- 封面优先本地 prepared cover
- 封面必须做约 `25%` 缩略图可读性检查，确认不是普通裸帧，也不是标题不可读
- 如果平台状态是 `审核中`、`修改审核中`、`pending` 或 `暂未可见`，不要直接重发
- 如果视频字幕不是模型直接生成的单行白字透明底版本，不进入发布
- 不以“点击发布”作为成功
- 抖音最终成功以 `作品管理` 列表顶行真实条目为准
- 视频号最终成功以 `视频管理` 列表顶行真实条目为准
