# Automation Runbook

这组自动化负责三件事:

1. 持续扫描本机自定义 skill 的新增、修改、删除
2. 每晚把当日变化整理成 Windows 可用版本的补全任务
3. 在 Mac / Windows 两侧都齐全后，按仓库分支自动提交并推送到 GitHub

## 监控范围

- `/Users/baishangjituan/.codex/skills/`
- `/Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/skills/`
- `/Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/automation/`

## 记录文件

- `skill-change-monitor.md`
  - 记录新增、修改、删除的 skill 文件
  - 重点记录 `SKILL.md`、引用文档、脚本、以及新建 `.py` 文件
- `windows-translation-status.md`
  - 记录 Windows 转译是否完成
  - 记录缺失项、阻塞项、以及已补齐内容
- `github-sync-status.md`
  - 记录是否已按分支完成提交和推送

## 分支约定

- Mac / 通用 Python 主线同步: `codex/default-python-sync`
- Windows 专用补全线: `codex/windows-version-20260411`

## 运行顺序

1. 小时级监控先发现变化
2. 每天 22:00 汇总变化并转译 Windows 版本
3. 每天 00:00 在 Windows 和 Mac 版本都齐全时执行 GitHub 提交和推送
