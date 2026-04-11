# Windows 专用版说明

这份说明不是“把 mac 文档里的路径替换一下”。

它的目标是:

- 把这套仓库补成 Windows 可复制版本
- 明确 Windows 上飞书桥接怎么装
- 明确浏览器自动化在 Windows 上哪些逻辑相同，哪些地方要改

## 1. 先说结论

这套仓库现在可以同时支持:

- macOS 版
- Windows 版

真正差异主要在两层:

1. 飞书桥接的本地后台运行方式
2. 少量浏览器自动化快捷键和路径约定

内容包、平台 SOP、发布日志、复盘结构本身并不因为系统不同而变化。

## 2. Windows 版现在已经补了什么

### A. 飞书桥接 Windows 部署脚本

位置:

- `skills/codex-feishu-bridge-skill/scripts/install_bridge_template_windows.ps1`
- `skills/codex-feishu-bridge-skill/assets/template/scripts/*.ps1`

当前已经包含:

- 安装脚本
- 启动脚本
- 停止脚本
- 状态查看脚本
- 日志查看脚本
- 通知 chat id 写入脚本
- 可选 startup task 注册脚本

### B. Windows 部署文档

位置:

- `skills/codex-feishu-bridge-skill/references/deployment-windows.md`
- `skills/codex-feishu-bridge-skill/references/INSTALL-QUICKSTART-WINDOWS.md`

### C. Python 自动接管的跨平台修正

当前已经补了:

- Windows 下 `Control+A`
- macOS 下 `Meta+A`

这意味着 `快手 v0.1` 不再只适配 Mac 键盘逻辑。

## 3. Windows 上推荐的目录

建议:

```text
C:\codex-feishu-bridge
```

以及:

```text
C:\content-pipeline
```

尽量不要把桥接或仓库放在带很多空格、中文过深层级、同步盘冲突目录里。

## 4. Windows 上浏览器执行要点

### 不变的

- 先写内容包，再开后台
- 先看管理页，再决定是否继续草稿
- 不以“点了发布”作为成功
- 成功判断仍然看管理页 / 公开页 / 列表页

### 变化的

- 快捷键从 `Meta` 切到 `Control`
- 本地路径从 `/Users/...` 变成 `C:\...`
- 飞书桥接后台不再走 `launchd`

## 5. 当前 Windows 版最适合怎么用

推荐顺序:

1. 先部署 Windows 飞书桥接
2. 先用 Windows 版继续内容打包和日志回填
3. 再用 `快手 v0.1` 做第一个平台试点
4. 再把同一套映射继续补到头条号和微信视频号

## 6. 这一版的边界

现在已经不是“只有 Mac 能看懂、能装”的仓库了。

但也还没到“Windows 8 平台一键全自动”的程度。

当前最准确的表述是:

- Windows 部署链路已补齐
- Windows 桥接脚本已补齐
- Windows 自动接管试点已开始可执行
- 多平台 Windows 全量自动化仍需继续补 selector 和实机验证
