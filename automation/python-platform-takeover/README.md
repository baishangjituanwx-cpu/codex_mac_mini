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
  - `微信视频号 v0.1`
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

```bash
cd automation/python-platform-takeover
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
playwright install chromium
```

## 环境变量

复制:

```bash
cp .env.example .env
```

核心变量:

- `BROWSER_CDP_URL`
- `BROWSER_USER_DATA_DIR`
- `RUN_HEADLESS`

如果你要“接管现有标签页”，优先走 `BROWSER_CDP_URL`。

## 示例命令

查看某个平台的接管规则:

```bash
python -m social_publisher readiness wechat_channels
```

查看当前浏览器里有哪些标签页:

```bash
python -m social_publisher inspect-tabs --url-contains channels.weixin.qq.com
```

验证内容包是否可读:

```bash
python -m social_publisher validate-package configs/content-package.example.yaml
```

尝试进入发布入口:

```bash
python -m social_publisher publish \
  --platform kuaishou \
  --package configs/content-package.example.yaml \
  --execute
```

注意:

当前状态分两层:

- 所有平台:
  - 都支持 readiness / inspect-tabs / validate-package
- 快手 / 头条号 / 微信视频号:
  - 已经接上 `--execute` 的真实接管链路
  - 都会先查管理页或列表页避免重复
  - 再接管发布页 / 草稿页
  - 最后回管理页或列表页验证
- 其他平台:
  - 还停留在脚手架阶段

如果只是想先看规则，不加 `--execute`。
