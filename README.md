# Multi-Platform Content Pipeline

这是一套可复制的多平台内容运营仓库，按当前工作区里最近成功跑通的流程重新整理，目标是让你后续上传 GitHub 后，可以快速在另一台机器复刻。

## 这份仓库包含什么

- `skills/codex-feishu-bridge-skill/`
  - 可部署的 Codex <-> 飞书桥接技能包
  - 内含 Node bridge、`launchd` 模板、部署脚本、使用文档
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
- `docs/`
  - 系统架构
  - 浏览器操作 SOP
  - 接管现有标签页执行手册
  - 最近成功流程时间线
  - GitHub 上传前检查表
- `scripts/init_campaign.js`
  - 一键初始化新 campaign 的内容包和日志骨架

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

然后按 skill 自带部署方式安装到目标机:

```bash
bash scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
cd "$HOME/.codex-feishu-bridge"
npm install
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
./scripts/bridge-start.sh
```

桥接跑起来后，在飞书聊天里执行:

```text
/setnotifyhere
/setprogresshere
```

这样发布完成推送和任务进度推送都会落到当前聊天。

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

建议把第一个试点先放在:

1. 快手
2. 头条号
3. 微信视频号
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
