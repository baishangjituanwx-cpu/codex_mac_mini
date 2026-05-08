# 小云雀源视频 API 对接手册

## 1. 定位

小云雀在这套工作流里仍然是上游源视频生成器，不是最终发布器。

当前唯一生成路径是 API 对接：

- 官方接入文档：`https://bytedance.larkoffice.com/wiki/JUlowWl8Bi6X8fkTKrYc70zRnVc`
- 本机官方 API skill：`/Users/baishangjituan/.codex/skills/xyq-nest-skill/SKILL.md`

不要再通过小云雀 / 剪映网页版操作生成任务。网页任务链接只用于查看，不用于 Codex 执行。

## 2. 必要环境

必须配置：

- `XYQ_ACCESS_KEY`

Windows PowerShell 等价写法：

```powershell
$env:XYQ_ACCESS_KEY = "your-access-key"
```

可选配置：

- `XYQ_OPENAPI_BASE`
- `XYQ_BASE_URL`

默认 base URL：

- `https://xyq.jianying.com`

安全规则：

- 不要把 Access Key 写进技能文件、脚本、日志或最终回复。
- 执行命令时优先使用环境变量。
- 如果缺少 `XYQ_ACCESS_KEY`，停止并提示用户配置；不要退回网页版。

## 3. API 脚本入口

官方 API skill 提供 4 个脚本：

```bash
python3 /Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/submit_run.py --message "生成一个 5 秒短视频"
```

Windows PowerShell repo mirror equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\submit_run.ps1 --message "生成一个 5 秒短视频"
```

```bash
python3 /Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/get_thread.py --thread-id THREAD_ID --run-id RUN_ID --after-seq 0
```

Windows PowerShell repo mirror equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\get_thread.ps1 --thread-id THREAD_ID --run-id RUN_ID --after-seq 0
```

```bash
python3 /Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/upload_file.py /path/to/reference.png
```

Windows PowerShell repo mirror equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\upload_file.ps1 "C:/Users/alice/Downloads/reference.png"
```

```bash
python3 /Users/baishangjituan/.codex/skills/xyq-nest-skill/scripts/download_results.py --urls URL1 URL2 --output-dir ./xyq_output --prefix artifact
```

Windows PowerShell repo mirror equivalent:

```powershell
.\skill-center\skills\xyq-nest-skill\scripts\download_results.ps1 --urls URL1 URL2 --output-dir "C:/Users/alice/Downloads/xyq_output" --prefix artifact
```

底层接口：

- `POST /api/biz/v1/skill/submit_run`
- `POST /api/biz/v1/skill/get_thread`
- `POST /api/biz/v1/skill/upload_file`

鉴权：

- `Authorization: Bearer <XYQ_ACCESS_KEY>`

## 4. 标准生成流程

### 文生视频

1. 检查 `XYQ_ACCESS_KEY` 是否存在。
2. 调用 `submit_run.py --message "<用户原始需求>"`。
3. 保存返回的 `thread_id`、`run_id`、`web_thread_link`。
4. 向用户展示 `web_thread_link`，但继续通过 API 轮询。
5. 每 10 秒左右调用 `get_thread.py`。
6. 如果返回意图确认或问题，转述给用户并等待回复。
7. 用户回复后，用同一个 `thread_id` 再次 `submit_run.py`。
8. 任务完成后提取产物 URL。
9. 用 `download_results.py` 下载到本地。
10. 对本地视频做源素材 QA。

### 参考图 / 参考视频生成

1. 确认本地文件存在。
2. 只接受图片和视频文件，单文件小于 200MB。
3. 每个文件调用一次 `upload_file.py`。
4. 收集返回的 `asset_id`。
5. 调用 `submit_run.py --message "<用户原始需求>" --asset-ids <asset_id...>`。
6. 进入标准轮询、下载、QA 流程。

### 继续已有会话

1. 复用已有 `thread_id`。
2. 调用 `submit_run.py --message "<新增需求>" --thread-id <thread_id>`。
3. 使用新的 `run_id` 轮询。

## 5. 用户侧 Agent 的边界

用户侧 Agent 只做四件事：

1. 上传用户给的参考文件，拿到 `asset_id`。
2. 把用户原始需求作为 `message` 提交。
3. 轮询并转述过程信息、问题和结果。
4. 下载产物，做本地 QA 和后续封面/发布交接。

不要做：

- 不要替用户扩写复杂 prompt，除非用户明确要求 prompt package。
- 不要手工拆分镜、拆镜头、拆多轮任务后再提交。
- 不要把一次完整需求拆成多次无必要 API run。
- 不要绕过 API 去网页点击、上传、下载或提取链接。

## 6. Founder 视频默认标准

适用场景：

- 大陈 founder-IP 口播
- 方法型短视频
- 30 秒左右
- 9:16 竖屏
- 中文口播
- 写实办公、会议、门店或业务场景

人物层级：

- 大陈：主角、主讲、主要出镜人物
- 小丽：助理、辅助角色、短暂出镜
- 不做双主角
- 如果双人物导致身份不稳，优先减少小丽镜头

默认参考图：

- 大陈：`/Users/baishangjituan/Downloads/素材/小云雀/人物素材/大陈.jpg`
- 小丽：`/Users/baishangjituan/Downloads/素材/小云雀/人物素材/小丽.png`

回退路径：

- `/Users/baishangjituan/Downloads/素材/小云雀/大陈.jpg`
- `/Users/baishangjituan/Downloads/素材/小云雀/小丽.png`

这些文件要通过 `upload_file.py` 变成 `asset_id` 后再随请求提交。

Windows handoff 时，把这些路径改成 quoted `C:/...` 绝对路径，不要继续沿用 `/Users/...` 示例。

## 7. 提示词包模式

当用户明确要求“帮我写小云雀提示词 / 改提示词 / 输出 prompt package”时，先读：

- `references/prompt-template.md`

输出顺序：

1. `主题文案`
2. `封面制作专用文案`
3. `核心母题`
4. `核心判断`
5. `建议口播内容`
6. 可作为 API `message` 发送的完整提示词
7. 必要的 QA 清单

提示词包只是准备 `message`，不是网页粘贴说明。

## 8. 轮询与终态

默认轮询：

- 每 10 秒一次
- 用 `after_seq` 做增量拉取
- 单次查询失败可以重试 1 次
- 连续 3 次失败后停止并说明错误

正常进行中：

- API 返回 run 仍在执行
- 过程消息持续更新
- 后端要求用户补充意图或回答问题

成功：

- run 完成
- messages / content / artifact 中出现可下载图片或视频 URL
- 下载到本地后可打开

失败：

- API 明确返回失败状态
- Access Key 无效
- 账号非订阅会员
- 积分不足
- 上传文件类型或大小不支持
- 服务异常

失败时必须报告 API 给出的错误信息。不要改用网页版重试。

## 9. 源素材 QA

下载后先做源素材 QA，不要直接发平台。

合格标准：

1. 人物仍然像目标人物。
2. 场景符合业务语境。
3. 字幕适合手机阅读。
4. 有清晰可截图的封面帧。

不合格信号：

- 人脸明显漂移
- 眼镜、发型、脸型不稳
- 头被裁掉
- 全身远景太多
- 画面像讲台、舞台或广告片
- 办公/门店/业务场景不真实
- 字幕太长
- 没有可用封面帧

出现这些问题时，优先用同一 `thread_id` 追加修改要求或重新发起 API 生成。

## 10. 出片后交接

如果视频用于多平台发布：

1. 先确认下载产物可播放。
2. 做源素材 QA。
3. 准备本地 `3:4` 竖版封面和 `4:3` 横版封面。
4. 对封面不稳定的平台，把竖版 title poster 前置到视频前 1 到 2 秒。
5. 再进入平台发布技能。

发布前必须检查目标平台管理列表，避免重复发布。
