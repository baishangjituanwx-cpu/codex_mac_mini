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
- 封面裁切结果需要人工确认
- 发布按钮点击后，没有出现成功信号，也没有在管理页看到新条目

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
