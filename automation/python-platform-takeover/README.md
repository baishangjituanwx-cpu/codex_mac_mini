# Python Platform Takeover

这是多平台发布仓库里的 Python 自动接管脚手架。

它的定位不是“今天就能 8 平台全自动一键发完”，而是先把下面 4 件事做统一:

1. 内容包输入格式
2. 浏览器接管方式
3. 平台规则元数据
4. 后续逐个平台补真实发布器的工程骨架

## 最短首跑

如果你刚从 GitHub 打开这个仓库，先不要自己拼命令，直接跑首跑脚本。

macOS:

```bash
cd automation/python-platform-takeover
bash scripts/quickstart-mac.sh --platform wechat_channels
```

Windows PowerShell:

```powershell
Set-Location automation/python-platform-takeover
.\scripts\quickstart-windows.ps1 -Platform wechat_channels
```

这两条脚本会自动帮你做 6 件事:

1. 创建 `.venv`
2. 安装 Python 依赖
3. 安装 Playwright Chromium
4. 生成 `.env`
5. 生成 `configs/content-package.local.yaml`
6. 运行 `doctor`、`inspect-tabs` 和安全模式 `publish`

如果你只是想单独检查环境，不想立刻走完整首跑，也可以直接用:

```bash
./scripts/social-publisher.sh doctor --package configs/content-package.local.yaml --platform wechat_channels --check-browser
```

## 当前状态

- 已完成:
  - Python 项目结构
  - 内容包加载器
  - CDP 接管浏览器骨架
  - 平台规则注册表
  - 平台 readiness 清单输出
- 未完成:
  - 每个平台稳定 selector
  - 风控检查点恢复
  - 其余平台的真正发布动作实现
- 已有可执行试点:
  - `快手 v0.1`
  - `头条号 v0.1`
  - `微博 v0.1`
  - `百家号 v0.1`
  - `知乎 v0.1`
  - `抖音 v0.1`
  - `微信视频号 v0.1`
  - 这 7 个平台都已补上“旧标签页残留旧草稿时停止接管”的保护
  - 其中快手、头条号、抖音已补上“发布页成功信号 + 管理页重试验证”的双层兜底
  - 通过 `--execute` 进入真实接管流程
  - 默认仍保持安全模式，不会直接点击发布

## 目录

```text
automation/python-platform-takeover/
├── .env.example
├── configs/
│   ├── content-package.demo.yaml
│   ├── content-package.example.yaml
│   └── platforms.example.yaml
├── pyproject.toml
├── README.md
├── scripts/
│   ├── quickstart-mac.sh
│   ├── quickstart-windows.ps1
│   ├── social-publisher.sh
│   ├── social-publisher.ps1
│   ├── start-chrome-cdp.sh
│   └── start-chrome-cdp.ps1
├── social_publisher/
│   ├── __init__.py
│   ├── __main__.py
│   ├── browser.py
│   ├── cli.py
│   ├── content_package.py
│   ├── doctor.py
│   ├── env.py
│   └── platforms/
│       ├── __init__.py
│       ├── base.py
│       ├── baijiahao.py
│       ├── douyin.py
│       ├── kuaishou.py
│       ├── toutiao.py
│       ├── wechat_channels.py
│       ├── weibo.py
│       ├── xiaohongshu.py
│       └── zhihu.py
└── tests/
    ├── test_browser_controller.py
    ├── test_content_package.py
    ├── test_doctor.py
    ├── test_env.py
    └── test_platform_base.py
```

## 安装

macOS / Linux:

```bash
cd automation/python-platform-takeover
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
playwright install chromium
```

如果本机自带的 `python3` 还是 `3.9`，先换到 `3.10+` 再继续。这个项目当前不支持 `Python 3.9`。

Windows PowerShell:

```powershell
Set-Location automation/python-platform-takeover
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m playwright install chromium
```

仓库里的 `.\scripts\social-publisher.ps1` 现在会先检查 `Python 3.10+` 和关键依赖是否已安装，缺了会直接给出友好提示。

macOS / Linux 也有对应包装器:

```bash
./scripts/social-publisher.sh doctor
```

## 直接使用的准确含义

这批脚本不是 Windows 专属，`Mac` 和 `Windows` 都可以直接使用。

但它的“直接使用”准确含义是:

- 通过 `CDP` 接管你已经打开并已登录的 Chromium 浏览器
- 读取当前标签页状态
- 继续接管发布页、草稿页或管理页

不是:

- 帮你从零创建登录态
- 绕过验证码或风控
- 保证 7 个平台在任何 UI 变动下都零维护

## 启动浏览器

### macOS

推荐单独开一个 Chrome profile:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.codex-chrome-takeover"
```

如果 `./scripts/start-chrome-cdp.sh` 提示 “CDP did not become reachable”，通常说明当前 Chrome 实例没有按预期挂上调试端口。先关闭冲突的 Chrome / Edge 实例，或换一个新的 `--profile-dir` 再试。

### Windows PowerShell

仓库已附带 PowerShell 启动器，会优先寻找 Chrome，也兼容 Edge:

```powershell
.\scripts\start-chrome-cdp.ps1
```

如果要指定端口或 profile 目录:

```powershell
.\scripts\start-chrome-cdp.ps1 -Port 9222 -ProfileDir "$HOME\.codex-chrome-takeover"
```

如果脚本提示 CDP 端口没有起来，先关闭冲突的浏览器实例，或者换一个新的 `-ProfileDir` 后再试。

如果当前已经有带登录态、且 CDP 可达的 Chrome / Edge，不要为了这套脚手架额外重启浏览器。优先把 `.env` 里的 `BROWSER_CDP_URL` 指到现有实例，直接复用当前登录会话；只有在用户明确同意时，才关闭或重开现有浏览器。

然后在这个浏览器里手动登录各平台后台，并把待接管页面保持打开。

## 环境变量

复制:

macOS / Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

CLI 现在会自动读取当前目录下的 `.env`，不需要再手动 `export` 一遍。

核心变量:

- `BROWSER_CDP_URL`
- `BROWSER_USER_DATA_DIR`
- `RUN_HEADLESS`
- `DEFAULT_TAKEOVER_MODE`

如果你要“接管现有标签页”，优先走 `BROWSER_CDP_URL`。

推荐值:

```bash
BROWSER_CDP_URL=http://127.0.0.1:9222
DEFAULT_TAKEOVER_MODE=existing-tab
RUN_HEADLESS=false
```

Windows 上如果要在 YAML 或 `.env` 中写素材绝对路径，优先使用正斜杠格式，例如 `C:/Users/name/Desktop/video.mp4`，这样最不容易踩转义问题。

## 准备内容包

macOS / Linux:

```bash
cp configs/content-package.example.yaml configs/content-package.local.yaml
```

Windows PowerShell:

```powershell
Copy-Item configs/content-package.example.yaml configs/content-package.local.yaml
```

需要至少填好:

- `campaign_id`
- `assets.main_video`
- `assets.cover_3_4`
- `assets.cover_4_3`
- 对应平台的 `title`
- 对应平台的 `description`

素材路径建议都写绝对路径。

如果你是从仓库里拿日期化的现成样例开工，例如 `configs/content-package.2026-04-27-platform-execution-verify-before-republish.yaml` 或 `configs/content-package.2026-04-30-repair-existing-not-republish.yaml` 这类文件里已经写死了 macOS 的 `/Users/...` 路径，不要直接在 Windows 上原样复用。先复制到你自己的 `configs/content-package.local.yaml` 或新的 `configs/content-package.<campaign>.yaml`，再把下面这些路径一起改成真实存在的 `C:/...` 或其他 Windows 绝对路径，平台文案和发布约束保持不变即可:

- `assets.*`
- `supporting_files.*`
- `platforms.<platform>.upload_plan.*`

如果上游内容包来自今天更新过的 `seedance-video-api` 流程，Windows 下还要额外遵守这 6 条交接规则:

- 不要把“视频已生成 + 封面已出图”误当成完成；只有平台文案包也落地后，才能继续往 `ready_for_publish` 走。
- 先把最终版平台文案落到 markdown 内容包，例如 `content-library/posts/shared/<campaign>-all-platform-publish-package.md` 或 `content-library/posts/video/<campaign>-video-publish-package.md`；如果仓库里暂时没有这两个目录，就在当前 campaign 工作目录按同样命名新建。
- 同一批交付里必须补一份逐平台上传矩阵，例如 `platform-upload-map.md`；每个平台都要写清楚 `上传视频` 或 `不上传视频`、上传封面路径、最终标题字段、以及最终文案或正文来源，不能让 Windows 发布线程靠猜。
- 再把同一份最终文案镜像进 `configs/content-package.local.yaml` 或日期化的 `configs/content-package.<campaign>.yaml`，字段映射保持一致:
  - `platforms.wechat_channels.title` = 视频号 `短标题`
  - `platforms.wechat_channels.description` = 视频号 `描述`
  - `platforms.weibo.title` / `description` = 微博视频 `标题` / `配文`
  - `platforms.douyin` / `kuaishou` / `baijiahao` / `toutiao` / `zhihu` / `xiaohongshu` 继续写各自最终 `标题` / `文案或正文`
- 如果这是准备交给 Hermes 的 `ready_for_publish` 包，Windows 侧还要保留同一套防重发字段，不要在本地改写或删掉:
  - `fingerprints.title_hash`
  - `fingerprints.body_core_hash`
  - `fingerprints.video_sha256`
  - `fingerprints.cover_sha256`
  - `lock_dir`
- 如果同一条 Seedance 主视频会复用到多个视频平台，要在矩阵里明确写出来；其中 头条号 / 小红书 默认按视频发布处理，只有用户明确要求图文派生稿时，才把对应平台写成 `不上传视频`。
- 真正进入发布页前，先锁定当前 `campaign_id`，并对将要提交的 4 项内容做读回确认: 视频路径、封面路径、最终标题或短标题、最终描述或正文。不要因为上一轮 receipt、旧草稿或旧管理页行还在，就跳过本轮包的读回。
- 如果当前内容包还没有自己的 receipt，先用 `.\scripts\social-publisher.ps1 record-receipt <你的 YAML> --platform <platform> --status not_started` 初始化；`receipt-status`、`record-receipt`、`validate-package` 都直接指向当前这份日期化 YAML 或 `content-package.local.yaml`，不要借用旧 campaign 的文件名。
- 如果仓库里同步有 `state/hermes-handoff/latest.json`，Windows 侧要确认它仍然指向当前这条真实 `ready_for_publish` campaign；不要让 smoke-test 包、`/tmp` scratch 包或只做校验的占位包抢走 latest 指针。
- Windows 侧只有在 markdown 文案包、上传矩阵都已存在，且 `.\scripts\social-publisher.ps1 validate-package configs/content-package.local.yaml` 或对应日期化 YAML 校验通过后，才算完成今天新增的 `ready_for_publish` 交付标准。

如果今天接到的是 handoff-only 包，例如 YAML 里已经写了 `publish_constraints.allow_live: false`、`no_publish_in_handoff_generation: true`、`no_upload_in_handoff_generation: true` 或 `no_submit_click_in_handoff_generation: true`，Windows 侧不要把它当成可直接发布的 live 包:

- 先用 `.\scripts\social-publisher.ps1 validate-package <你的 YAML>` 确认路径、标题和文案字段齐全。
- 用 `.\scripts\social-publisher.ps1 receipt-status <你的 YAML> --platform <platform>` 查看当前 campaign 是否已经有 receipt；没有的话用 `record-receipt --status not_published` 初始化占位。
- 这类包的目标是交接，不是实发；不要跑 `publish --execute`，不要打开原生文件选择器，不要点平台提交按钮。
- 如果仓库里同步有 `state/hermes-handoff/latest.json` 指向同一个 `campaign_id`，把它和当前 receipt 一起当成 Windows 侧后续接力的唯一入口，不要绕回旧 campaign 或旧 receipt。

## 示例命令

macOS / Linux:

```bash
./scripts/social-publisher.sh doctor --package configs/content-package.local.yaml --platform wechat_channels --check-browser
python -m social_publisher readiness wechat_channels
python -m social_publisher inspect-tabs --url-contains channels.weixin.qq.com
python -m social_publisher inspect-tabs --platform wechat_channels --package configs/content-package.local.yaml
python -m social_publisher validate-package configs/content-package.example.yaml
python -m social_publisher publish kuaishou configs/content-package.local.yaml --execute
social-publisher publish kuaishou configs/content-package.local.yaml --execute
```

Windows PowerShell:

```powershell
.\scripts\social-publisher.ps1 doctor --package configs/content-package.local.yaml --platform wechat_channels --check-browser
.\scripts\social-publisher.ps1 readiness wechat_channels
.\scripts\social-publisher.ps1 inspect-tabs --url-contains channels.weixin.qq.com
.\scripts\social-publisher.ps1 inspect-tabs --platform wechat_channels --package configs/content-package.local.yaml
.\scripts\social-publisher.ps1 validate-package configs/content-package.example.yaml
.\scripts\social-publisher.ps1 publish kuaishou configs/content-package.local.yaml --execute
```

新增的 `inspect-tabs --platform ... --package ...` 会按平台规则给现有标签页打分，输出:

- 哪个 tab 最像这次要接管的草稿
- 哪些字段已经和发布包匹配
- 哪些 tab 属于旧草稿、登录页或缺关键 frame，应该停止接管

针对今天补强过的 `wechat_channels` 规则，Windows 不需要单独维护第二套发布逻辑:

- 直接走 `.\scripts\social-publisher.ps1 publish wechat_channels configs/content-package.local.yaml --execute`
- 共享清空重输逻辑会在 Windows 自动使用 `Control+A`，在 macOS 自动使用 `Meta+A`
- 视频号封面上传在 Windows / macOS 共用同一套真实上传链路: 只对 `accept*="image"` 的图片输入框做真实文件注入，不伪造 `input.files`
- 如果 Browser Bridge / OpenCLI 暂时够不到真实编辑器，但已登录的 `platform/post/create` 页面就在前台 Chrome 里，Windows 允许走短临时路径回退，不过必须先复制成真实文件:

```powershell
Copy-Item C:/content-pipeline/video.mp4 "$env:TEMP\\vhvideo-real.mp4" -Force
Copy-Item C:/content-pipeline/cover.png "$env:TEMP\\vhcover-standard.png" -Force
```

- 走这条回退时，不要用 Explorer 搜索结果、`.lnk` 快捷方式、OneDrive 占位文件或 symlink；直接把 `$env:TEMP\\vhvideo-real.mp4` / `$env:TEMP\\vhcover-standard.png` 这种短真实路径粘进 Windows 文件选择器的“文件名”输入框，再点 `打开`
- 如果同一轮里 `platform/post/list` 标签页也开着，每次传文件、写字段、点 `发表` 前都重新确认当前活动页还是 `platform/post/create`
- Shadow DOM 字段映射在 Windows / macOS 一致: `视频描述` 走 shadow-root `.input-editor`，`短标题` 走 `input[placeholder="概括视频主要内容，字数建议6-16个字符"]`，写入后必须从同一 shadow root 精确回读
- 提交时两端都必须点真实 `button` `发表`；只点外层 wrapper `DIV` 不算成功提交
- `微信视频号` 的成功标准在两端一致: 发布前要求 `短标题` / `视频描述` 精确回读，发布后要求管理页最新一条同时通过 `shortTitle` / `description` / 封面缩略图二次复核

针对 `2026-04-23` 新增的本地发布台账 / 近似重复拦截规则，Windows 直接复用同一套 CLI 包装器:

- 先查本地台账:

```powershell
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform wechat_channels
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform xiaohongshu
```

- 针对 `2026-04-28` 新增的“新 campaign 先锁包、缺 receipt 先初始化、旧 receipt 只算历史证据”规则，Windows 侧也不要另造第二套流程:
  - 先确认你当前要发的就是最新 `ready_for_publish` 内容包，并且它自己的 `campaign_id` 已经写进 `configs/content-package.local.yaml` 或当天的 `configs/content-package.<campaign>.yaml`
  - `receipt-status` 只会读取当前内容包 `campaign_id` 对应的 `state/publish-receipts/<campaign_id>.json`；昨天或上一轮 campaign 的 receipt 就算是 `published`，也不能当今天新包的成功证据
  - 如果当前内容包还没有 receipt，先初始化成 `not_started`，再进平台管理页或发布页，避免把“缺台账”误判成“可以沿用上一轮”

```powershell
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform wechat_channels
.\scripts\social-publisher.ps1 record-receipt configs/content-package.local.yaml --platform wechat_channels --status not_started
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform wechat_channels
```

- 如果你今天切到了新的 `campaign_id`，不要复制旧的 receipt 文件名继续用；让 `record-receipt --status not_started` 为新 campaign 生成新的 `state/publish-receipts/<campaign_id>.json`，旧 receipt 只留作历史留痕。
- 对 `social-publish-automation` / `wechat_channels` 今天新增的 anti-duplicate 规则，Windows 判断标准与 macOS 一致:
  - 先锁定当前内容包的 `campaign_id`、视频路径、封面路径、`短标题`、`视频描述`
  - 如果管理页里看到的是上一轮 campaign 的旧条，只能当历史证据，不能拿来挡住或放行今天的新包
  - 如果本轮内容包的 receipt 已经是 `submitted`、`published`、`under_review`、`success` 或 `verified`，默认先停下，不要因为 UI 抖动就重复补发
  - 如果本轮内容包的 receipt 是 `blocked_account_review_pending`，把它当成平台账号审核阻断，不要清台账后硬重发；先等账号审核通过，或由用户明确改走别的发布方案
- `receipt-status` / `record-receipt` 现在会继续复用共享 Python loader；即使 `state/publish-receipts/<campaign_id>.json` 里新增了 `verified_fields`、`aid`、`object_nonce` 这类管理页核验字段，Windows 侧也不需要手工删键再跑命令。

- 如果手工确认旧内容已经删除、转私密或明确废弃，再清掉对应平台台账:

```powershell
.\scripts\social-publisher.ps1 clear-receipt configs/content-package.local.yaml --platform wechat_channels
.\scripts\social-publisher.ps1 clear-receipt configs/content-package.local.yaml --platform xiaohongshu
```

- 如果是手工路径已经成功且拿到了小红书 `share_link`，立刻补记本地台账，避免因为 `笔记管理` 延迟而重复发布:

```powershell
.\scripts\social-publisher.ps1 record-receipt configs/content-package.local.yaml --platform xiaohongshu --status success --share-link "https://www.xiaohongshu.com/..."
```

- 对 `2026-04-24` 新增的封面修复待复核场景，也直接用同一个台账命令查看，不要另开第二套 Windows 流程:

```powershell
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform wechat_channels
```

- 如果输出里出现下面这些 note，表示当前条目已经进入“先修原条、等复核，不要重发”的状态:
  - `newest_row_cover_thumbnail_present: true`
  - `cover_readability_passed: false`
  - `cover_repair_pending_final_thumbnail_review: true`
  - `cover_repair_status: 修改审核中...`
  - `receipt_status: verified_cover_repair_under_review`
- Windows 下执行视频号发布前，先把 `assets.cover_3_4` 缩到大约 `25%` 的列表卡片尺寸自行复核。通过标准不是“封面文件存在”，而是缩略图主标题仍可读，且人物主体明确可见。
- 如果管理列表里封面“有图但不可读”，不要重发同一个视频；直接对现有条目走 `修改描述和封面`，并保持 `verified_cover_repair_under_review` / 待复核状态，直到缩略图刷新后再次通过。
- Windows 下记录这类修复封面素材路径时，继续优先写 PowerShell 也能直接识别的绝对路径，例如 `C:/content-pipeline/covers/fixed-cover.png` 或 `C:\\content-pipeline\\covers\\fixed-cover.png`。
- 如果后续 `receipt-status` 或 `state/publish-receipts/<campaign_id>.json` 出现下面这些信号，说明视频号已经把原条目锁住，Windows 侧也不要继续强闯隐藏编辑路径:
  - `receipt_status: verified_cover_repair_failed_locked`
  - `cover_repair_edit_disabled: true`
  - `cover_repair_row_status: 作者修改过视频信息`
- 进入 `verified_cover_repair_failed_locked` 后，安全动作只有两种:
  - 等平台重新开放 `修改描述和封面`
  - 先人工删除 / 转私密 / 明确废弃旧条，再执行替换发布
- 如果旧条已经人工删除、隐藏或明确废弃，再按 Windows PowerShell 走替换发布，不要手抄第二套命令:

```powershell
.\scripts\social-publisher.ps1 clear-receipt configs/content-package.local.yaml --platform wechat_channels
.\scripts\social-publisher.ps1 publish wechat_channels configs/content-package.local.yaml --execute
.\scripts\social-publisher.ps1 receipt-status configs/content-package.local.yaml --platform wechat_channels
```

- 替换发布后如果本地台账显示这些信号，表示新的对象已经提交成功并进入平台审核，可通知但不要重复补发:
  - `receipt_status: under_review`
  - `publish_state_text: 处理中`
  - `publish_state_label: 处理中`
  - `new_object_id` 或新的管理行 `objectId`
  - `cover_key` / `new_cover_key`
- 这批状态码在 Windows / macOS 含义一致:
  - `stopped_receipt_duplicate`: 本地台账已经拦下同一 campaign 的重复补发
  - `stopped_recent_content_duplicate`: 视频号最近管理行已出现同 `短标题` 且正文高度相似的内容，必须先改标题或正文骨架
  - `stopped_duplicate`: 管理页已经存在同标题或同描述片段的条目，先处理旧条再继续
  - `verified_cover_repair_under_review`: 原视频已提交封面修复，但管理列表缩略图还没完成最终复核；此时继续修原条，不要重发新条
  - `verified_cover_repair_failed_locked`: 原视频封面修复失败且平台已锁定编辑；不要继续修原条，等平台重开或先处置旧条再替换发布
  - `blocked_account_review_pending`: 平台明确提示账号资料或权限仍在审核，当前账号被阻断发布；保留这条 receipt，等审核通过或用户明确改计划，不要把它当成“没开始”然后重发
  - `under_review`: 替换发布的新视频已经提交成功，平台仍在审核；此时等待管理列表复核，不要把它当成失败重发

注意:

当前状态分两层:

- 所有平台:
  - 都支持 doctor / readiness / inspect-tabs / validate-package
- 快手 / 头条号 / 微博 / 百家号 / 知乎 / 抖音 / 微信视频号:
  - 已经接上 `--execute` 的真实接管链路
  - 都会先查管理页或列表页避免重复
  - 再接管发布页 / 草稿页
  - 最后回管理页或列表页验证
- 其他平台:
  - 还停留在脚手架阶段

如果只是想先看规则，不加 `--execute`。

## 推荐使用顺序

第一次接管，建议按这个顺序:

1. `doctor`
2. `inspect-tabs`
3. `readiness`
4. 不带 `--execute` 的 `publish`
5. 带 `--execute` 的 `publish`

macOS / Linux:

```bash
./scripts/social-publisher.sh doctor --package configs/content-package.local.yaml --platform toutiao --check-browser
social-publisher inspect-tabs --url-contains mp.toutiao.com
social-publisher readiness toutiao
social-publisher publish toutiao configs/content-package.local.yaml
social-publisher publish toutiao configs/content-package.local.yaml --execute
```

Windows PowerShell:

```powershell
.\scripts\social-publisher.ps1 doctor --package configs/content-package.local.yaml --platform toutiao --check-browser
.\scripts\social-publisher.ps1 inspect-tabs --url-contains mp.toutiao.com
.\scripts\social-publisher.ps1 readiness toutiao
.\scripts\social-publisher.ps1 publish toutiao configs/content-package.local.yaml
.\scripts\social-publisher.ps1 publish toutiao configs/content-package.local.yaml --execute
```

## 遇到这些情况先停下来

- 平台弹出验证码
- 当前标签页残留的是另一篇旧草稿
- 管理页已经出现重复内容
- 视频号封面没有出现明确的已应用信号
- 发布按钮点击后，没有出现成功信号，也没有在管理页看到新条目
- 视频号管理页新条目没有同时通过内容级二次复核
  - 复核至少包括：目标描述片段命中管理页同一条记录
  - 发布前的短标题、描述回读与内容包完全一致
  - Windows PowerShell 入口和 macOS 共用同一套复核逻辑，不需要额外脚本分叉

## 本地运行复盘后，什么值得补充到 GitHub

值得补充的是可复用结论，不是原始运行痕迹。

优先入库的内容:

- 真实修复发布行为的代码
- 防止回归的测试
- 能解释接管规则的稳定文档

这类高价值结论通常包括:

- 先给现有发布页打分，再决定是否复用
- 旧草稿不匹配时直接停止接管
- 没有安全候选页时强制新开发布页
- 发布后既看成功信号，也回管理页复核

默认不要直接上传的内容:

- `~/.codex/sessions/**`
- `~/.codex/shell_snapshots/**`
- 本机数据库、缓存、终端原始输出
- 一次性排查快照或临时生成的监控快照

如果一次本地运行只是证明“某个规则已经在代码里实现并且测试覆盖了”，那就不需要再把那次运行记录单独上传到 GitHub。
