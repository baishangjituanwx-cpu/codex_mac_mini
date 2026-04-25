# Multi-Platform Content Pipeline

这是一套可复制的多平台内容运营仓库，按当前工作区里最近成功跑通的流程重新整理，目标是让你后续上传 GitHub 后，可以快速在另一台机器复刻。

## GitHub 打开后先做这一步

如果你希望“打开仓库后就立刻开始跑”，先从 Python 接管首跑入口开始。

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

这两条命令会自动完成:

- 环境安装
- `.env` 生成
- demo 内容包生成
- CDP 浏览器启动
- `doctor`
- `inspect-tabs`
- 安全模式 `publish`

跑完以后，你只需要替换素材路径、登录后台标签页，再加上 `--execute` 就能进入真实接管。

## 这份仓库包含什么

- `skills/codex-feishu-bridge-skill/`
  - 可部署的 Codex <-> 飞书桥接技能包
  - 内含 Node bridge、macOS `launchd` 模板、Windows PowerShell 模板、部署脚本、使用文档
- `skills/multi-platform-content-review-skill/`
  - 多平台发布后复盘 skill
  - 适合 nightly review、人工复盘、飞书复盘同步
- `workflow/content-library/`
  - 视频制作到多平台发布的内容模板
  - 发布日志模板
  - 最近成功案例示例
- `automation/python-platform-takeover/`
  - Python 自动接管脚手架
  - 先把“平台规则、接管条件、管理页验证标准”沉淀成统一工程
  - 方便后续逐个平台补齐真正可执行的接管脚本
  - 现在已经带 `quickstart-mac.sh`、`quickstart-windows.ps1`、`doctor`
- `skill-center/`
  - 本机 Codex 技能中心镜像
  - 当前已把 `~/.codex/skills/` 里的 `61` 个 skill 镜像进仓库
  - 提供 Mac / Windows 两套同步脚本，保证两边拿到完全相同的一套 skill
- `docs/`
  - 系统架构
  - 浏览器操作 SOP
  - 接管现有标签页执行手册
  - 最近成功流程时间线
  - GitHub 上传前检查表
- `scripts/init_campaign.js`
  - 一键初始化新 campaign 的内容包和日志骨架
- `scripts/dashboard-export-review.js`
  - 从复盘正文生成 8 平台 dashboard companion JSON
- `scripts/dashboard-doctor.js`
  - 检查 Node 版本、dashboard 环境变量、内容库路径和指定日期复盘文件
- `scripts/dashboard-sync-review.js`
  - 导出、校验、刷新 `latest.json`、上传远端 dashboard、写同步审计的一键入口
- `scripts/dashboard-sync.sh`
  - macOS / Linux 一键预检 + 同步入口
- `scripts/dashboard-sync.ps1`
  - Windows PowerShell 一键预检 + 同步入口
- `scripts/sync_remote_mempalace.sh`
  - 把当前仓库增量同步到远端 MemPalace 中心主机

## 当前实现方式

这点我直接说清楚:

- 飞书桥接和自动推送:
  - 是 Node 实现
  - 核心依赖 `@larksuite/cli`
  - 由本地 `codex` CLI 和 `src/bridge.js` 串起来
- 浏览器侧发布:
- 当前最近成功流程不是固定的 Python 发布脚本
- 而是 `Codex + 浏览器自动化会话` 执行
- 具体成功 SOP 已经整理到 [`docs/browser-operation-sop.md`](./docs/browser-operation-sop.md)
- 直接接管已有标签页、半成品草稿页、失败后恢复页的细粒度规则，整理到 [`docs/browser-tab-takeover-runbook.md`](./docs/browser-tab-takeover-runbook.md)
- Python 自动接管:
  - 这次补上了 `automation/python-platform-takeover/` 脚手架
  - 目前已经把平台级规则、接管前检查项、成功信号、工程结构统一下来
  - 快手已经补到 `v0.1` 可执行接管链路
  - 头条号、微博、百家号、知乎、抖音、微信视频号已经补到 `v0.1` 接管链路
  - 还没有把 8 个平台全部做成“可直接跑完全流程”的稳定脚本
- 数据复盘:
  - 当前主链路是 `发布包 Markdown + 发布日志 Markdown + review skill`
- 视频制作:
  - 当前仓库侧沉淀的是生产包、封面规则、下游发布包
  - 上游源视频生成仍然依赖外部工作台或浏览器工作流，不是这个仓库里的一键脚本

## 目录结构

```text
.
├── automation/
├── docs/
├── scripts/
├── skill-center/
├── skills/
│   ├── codex-feishu-bridge-skill/
│   └── multi-platform-content-review-skill/
└── workflow/
    └── content-library/
        ├── assets/
        ├── examples/
        ├── logs/
        ├── posts/
        └── templates/
```

## 快速开始

### 1. 准备 Codex + 飞书桥接

进入:

```bash
cd skills/codex-feishu-bridge-skill
```

macOS 安装:

```bash
bash scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
cd "$HOME/.codex-feishu-bridge"
npm install
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
./scripts/bridge-start.sh
```

Windows 安装:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_bridge_template_windows.ps1 -TargetDir C:\codex-feishu-bridge
cd C:\codex-feishu-bridge
npm install
.\node_modules\.bin\lark-cli.cmd config init --app-id <APP_ID> --app-secret-stdin --brand feishu
.\node_modules\.bin\lark-cli.cmd auth login --domain im,event --recommend
.\scripts\bridge-start.ps1
```

桥接跑起来后，在飞书聊天里执行:

```text
/setnotifyhere
/setprogresshere
```

这样发布完成推送和任务进度推送都会落到当前聊天。

Windows 专用入口文档见:

- [`docs/windows-version-guide.md`](./docs/windows-version-guide.md)
- [`skills/codex-feishu-bridge-skill/references/deployment-windows.md`](./skills/codex-feishu-bridge-skill/references/deployment-windows.md)

### 2. 初始化一个新内容批次

在仓库根目录运行:

```bash
node scripts/init_campaign.js --id 2026-04-11-ai-workflow --theme "这里写母题"
```

会自动生成:

- `workflow/content-library/posts/shared/...`
- `workflow/content-library/posts/video/...`
- `workflow/content-library/posts/weibo/...`
- `workflow/content-library/posts/xiaohongshu/...`
- `workflow/content-library/posts/baijiahao/...`
- `workflow/content-library/posts/toutiao/...`
- `workflow/content-library/posts/zhihu/...`
- 对应平台日志骨架

### 3. 先做内容，再开后台

按这个顺序走:

1. 先写 `campaign brief`
2. 再写 `production pack`
3. 再写 `all-platform publish package`
4. 再补各平台定制包
5. 最后才打开各平台后台

### 4. 浏览器执行发布

不要跳步骤，直接按 [`docs/browser-operation-sop.md`](./docs/browser-operation-sop.md) 走。

如果不是从空白后台开始，而是要接管已经开着的旧标签页、半成品页、失败后停住的页，直接看:

- [`docs/browser-tab-takeover-runbook.md`](./docs/browser-tab-takeover-runbook.md)

关键原则:

- 发布前先查管理页，避免重复投放
- 对富文本编辑器用真实输入，不信任单纯 DOM 赋值
- 提交成功不等于发布成功，必须回管理页验证
- 每个平台确认成功后，立即推一次飞书

### 5. 发布后复盘

完成日志回填后，用:

- `skills/multi-platform-content-review-skill/`
- `workflow/content-library/logs/`
- `workflow/content-library/posts/`

来做 batch review。

如果这轮复盘还要同步 8 平台 Docker 看板，用仓库根目录的一键命令:

```bash
npm run dashboard:sync -- --review-date YYYY-MM-DD
```

或者直接用平台包装器:

```bash
bash scripts/dashboard-sync.sh --review-date YYYY-MM-DD
```

```powershell
.\scripts\dashboard-sync.ps1 --review-date YYYY-MM-DD
```

首次接入先配置:

- [`.env.dashboard.example`](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/.env.dashboard.example>)
- [`docs/dashboard-sync-runbook.md`](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/docs/dashboard-sync-runbook.md>)
- [`docs/dashboard-upload-api-contract.md`](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/docs/dashboard-upload-api-contract.md>)

### 6. Python 接管脚本从这里开始

如果你准备把“接管现有标签页”逐步沉淀成独立 Python 工程，直接看:

- [`docs/python-automation-roadmap.md`](./docs/python-automation-roadmap.md)
- `automation/python-platform-takeover/`

当前这部分的定位很明确:

- 已有:
  - 统一工程目录
  - 内容包读取骨架
  - CDP 接管浏览器骨架
  - 各平台规则元数据
  - 快手 `--execute` 试点
  - 头条号 / 微信视频号 `--execute` 试点
- 暂未完成:
  - 每个平台稳定 selector
  - 风控检查点恢复逻辑
  - 真正可连续执行的发布实现

现在这块已经多了一条更适合 GitHub 首次使用的路径:

- Mac: `bash scripts/quickstart-mac.sh --platform wechat_channels`
- Windows: `.\scripts\quickstart-windows.ps1 -Platform wechat_channels`
- 单独自检: `doctor`

建议把第一个试点先放在:

1. 快手
2. 头条号
3. 微信视频号

### 7. Mac 直接使用说明

如果你现在就在 `Mac` 上跑这套 Python 接管脚本，可以直接按下面走。

先说边界:

- 这是“接管现有浏览器会话”的方案
- 不是从零启动一个全新匿名浏览器帮你登录所有平台
- 更不是 8 平台全部稳定量产的一键发布器

#### 7.1 你需要先准备好的东西

- `macOS` 本机
- `Python 3.10+`
- `Google Chrome` 或其他 Chromium 内核浏览器
- 已经登录好的平台后台
- 一份内容包 YAML
- 本地视频和封面素材绝对路径

#### 7.2 在 Mac 上启动一个可接管的浏览器

推荐单独开一个 Chrome profile，不要污染你日常浏览器。

示例命令:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.codex-chrome-takeover"
```

### 8. 数据看板同步

这套仓库现在已经把“复盘 -> 导出 -> 校验 -> 上传面板”收成了固定脚本链。

常用命令:

```bash
npm run dashboard:doctor -- --review-date YYYY-MM-DD
npm run dashboard:export -- --review-date YYYY-MM-DD
npm run dashboard:sync -- --review-date YYYY-MM-DD
```

双平台入口:

```bash
bash scripts/dashboard-sync.sh --review-date YYYY-MM-DD
```

```powershell
.\scripts\dashboard-sync.ps1 --review-date YYYY-MM-DD
```

注意:

- dashboard 上传不再内置任何默认 API 地址、账号组或管理员账号
- 先在仓库根目录创建 `.env.dashboard` 或 `.env.dashboard.local`
- 需要填写自己的 `DASHBOARD_API_BASE`、`DASHBOARD_ACCOUNT_NAME`、`DASHBOARD_ADMIN_USERNAME`、`DASHBOARD_ADMIN_PASSWORD`
- 仓库会自动兼容 `workflow/content-library` 和 `content-library` 两种内容库布局
- 预检命令会检查 `Node.js 18+`、环境变量和复盘文件是否齐全
- 固定 smoke test：`npm run dashboard:fixture`
- GitHub Actions 会自动跑 dashboard fixture smoke，防止脚本回归

启动后，用这个浏览器窗口手动登录你要发的平台。后面的 Python 脚本会通过 `CDP` 接管这组标签页。

#### 7.3 安装 Python 接管环境

```bash
cd automation/python-platform-takeover
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
playwright install chromium
cp .env.example .env
```

`.env` 里最关键的是:

- `BROWSER_CDP_URL=http://127.0.0.1:9222`
- `DEFAULT_TAKEOVER_MODE=existing-tab`

#### 7.4 准备内容包

先复制一份示例:

```bash
cp configs/content-package.example.yaml configs/content-package.local.yaml
```

然后至少改这几项:

- `campaign_id`
- `assets.main_video`
- `assets.cover_3_4`
- `assets.cover_4_3`
- 你要发布的平台标题和正文

这里的素材路径建议全部写绝对路径，少踩一次路径坑，心情会更好一点。

#### 7.5 先检查浏览器标签页是否接得上

```bash
source .venv/bin/activate
social-publisher inspect-tabs --url-contains channels.weixin.qq.com
```

如果能看到当前打开的后台标签页，说明 Mac 这边的 `CDP` 接管已经通了。

#### 7.6 先跑安全模式

先不要急着真发，先看规则:

```bash
social-publisher readiness wechat_channels
social-publisher publish wechat_channels configs/content-package.local.yaml
```

这一步默认只会输出 readiness 和接管条件，不会真实点击发布。

#### 7.7 再跑真实接管

确认浏览器里就是你要接管的那组登录态和标签页后，再执行:

```bash
social-publisher publish wechat_channels configs/content-package.local.yaml --execute
```

目前已经接上真实接管链路的平台有:

- `kuaishou`
- `toutiao`
- `weibo`
- `baijiahao`
- `zhihu`
- `douyin`
- `wechat_channels`

#### 7.8 Mac 直接使用时的几个硬规则

- 发布前先看管理页或列表页，避免重复发
- 旧标签页里如果残留的是别的草稿，脚本会停止接管
- 脚本点击了发布，不等于平台一定成功入库，还要看返回的验证结果
- 遇到验证码、风控、人工确认封面这类检查点，要人工接手

如果你想把“Mac 上直接使用”这条线继续稳定下来，优先做的是:

1. 用你自己的已登录浏览器标签页跑一轮 `inspect-tabs`
2. 先试 `wechat_channels / toutiao / kuaishou`
3. 跑完后把真实 selector 偏差和人工检查点补回代码
## 最近成功基线

当前这份仓库主要依据两条本地成功证据整理:

- `2026-04-08 ai-labor`
  - 全平台发布包、分平台发布包、日志最完整
  - 适合做“成功链路标准样本”
- `2026-04-10 ai-work-revalued`
  - 母题、标题矩阵、视频平台文案结构更清晰
  - 适合做“当前最新包装结构样本”

详细时间线见 [`docs/latest-success-flow.md`](./docs/latest-success-flow.md)。

## 媒体素材说明

示例里只保留了 Markdown 包和日志，真实视频、封面、字幕等二进制素材没有一起塞进这份 GitHub-ready 包。

实际使用时，把你自己的素材放到:

```text
workflow/content-library/assets/generated/<campaign-id>/
```

示例中的 `{{WORKSPACE_ROOT}}` 只是占位符，表示你的本机仓库根目录。

## 技能中心镜像

这次仓库里额外补上了一块之前明显缺失的内容:

- `skill-center/skills/`

它不是几个零散示例，而是把当前本机 `~/.codex/skills/` 里正在使用的 skill 做了一份完整镜像。

这意味着:

- GitHub 上现在能看到完整 skill 中心
- `Mac` 和 `Windows` 都可以从同一份镜像恢复 skill
- 像 `baijiahao-ops`、`douyin-ops`、`kuaishou-ops`、`social-publish-automation` 这类 skill，不再只存在于本机

如果你要把仓库里的 skill 中心同步到本机:

- Mac: `bash skill-center/scripts/sync-skills.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File .\skill-center\scripts\sync-skills.ps1`

## 安全和上传建议

- 不要提交:
  - `.bridge.env`
  - `bridge.log`
  - `bridge.stdout.log`
  - `bridge.stderr.log`
  - `.codex-feishu-bridge/`
  - 任意 chat id、app secret、验证码
- 上传前再看一遍:
  - [`docs/github-upload-checklist.md`](./docs/github-upload-checklist.md)
