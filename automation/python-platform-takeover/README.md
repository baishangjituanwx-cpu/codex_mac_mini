# Python Platform Takeover

这是多平台发布仓库里的 Python 自动接管脚手架。

它的定位不是“今天就能 8 平台全自动一键发完”，而是先把下面 4 件事做统一:

1. 内容包输入格式
2. 浏览器接管方式
3. 平台规则元数据
4. 后续逐个平台补真实发布器的工程骨架

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
│   ├── content-package.example.yaml
│   └── platforms.example.yaml
├── pyproject.toml
├── README.md
├── scripts/
│   ├── social-publisher.ps1
│   └── start-chrome-cdp.ps1
├── social_publisher/
│   ├── __init__.py
│   ├── __main__.py
│   ├── browser.py
│   ├── cli.py
│   ├── content_package.py
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
    └── test_content_package.py
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

Windows PowerShell:

```powershell
Set-Location automation/python-platform-takeover
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m playwright install chromium
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

### Windows PowerShell

仓库已附带 PowerShell 启动器，会优先寻找 Chrome，也兼容 Edge:

```powershell
.\scripts\start-chrome-cdp.ps1
```

如果要指定端口或 profile 目录:

```powershell
.\scripts\start-chrome-cdp.ps1 -Port 9222 -ProfileDir "$HOME\.codex-chrome-takeover"
```

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
python -m social_publisher readiness wechat_channels
python -m social_publisher inspect-tabs --url-contains channels.weixin.qq.com
python -m social_publisher validate-package configs/content-package.example.yaml
python -m social_publisher publish --platform kuaishou --package configs/content-package.local.yaml --execute
social-publisher publish kuaishou configs/content-package.local.yaml --execute
```

Windows PowerShell:

```powershell
.\scripts\social-publisher.ps1 readiness wechat_channels
.\scripts\social-publisher.ps1 inspect-tabs --url-contains channels.weixin.qq.com
.\scripts\social-publisher.ps1 validate-package configs/content-package.example.yaml
.\scripts\social-publisher.ps1 publish --platform kuaishou --package configs/content-package.local.yaml --execute
```

注意:

当前状态分两层:

- 所有平台:
  - 都支持 readiness / inspect-tabs / validate-package
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

1. `inspect-tabs`
2. `readiness`
3. 不带 `--execute` 的 `publish`
4. 带 `--execute` 的 `publish`

macOS / Linux:

```bash
social-publisher inspect-tabs --url-contains mp.toutiao.com
social-publisher readiness toutiao
social-publisher publish toutiao configs/content-package.local.yaml
social-publisher publish toutiao configs/content-package.local.yaml --execute
```

Windows PowerShell:

```powershell
.\scripts\social-publisher.ps1 inspect-tabs --url-contains mp.toutiao.com
.\scripts\social-publisher.ps1 readiness toutiao
.\scripts\social-publisher.ps1 publish --platform toutiao --package configs/content-package.local.yaml
.\scripts\social-publisher.ps1 publish --platform toutiao --package configs/content-package.local.yaml --execute
```

## 遇到这些情况先停下来

- 平台弹出验证码
- 当前标签页残留的是另一篇旧草稿
- 管理页已经出现重复内容
- 封面裁切结果需要人工确认
- 发布按钮点击后，没有出现成功信号，也没有在管理页看到新条目
