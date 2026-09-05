# Automation Runbook

这组自动化负责三件事:

1. 持续扫描本机自定义 skill 的新增、修改、删除
2. 每晚把当日变化整理成 Windows 可用版本的补全任务
3. 在 Mac / Windows 两侧都齐全后，按仓库分支自动提交并推送到 GitHub

## 监控范围

- `/Users/baishangjituan/.codex/skills/`
- `/Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/skills/`
- `/Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/skill-center/`
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

## 哪些内容应该进 GitHub

优先上传这三类稳定产物:

- 真正修复或补强行为的代码
- 能解释长期规则的文档
- 能兜住回归的测试

如果本地运行只暴露了一个可复用的工程结论，例如“旧草稿页不该误接管”或“没有合格候选页时应强制新开发布页”，应该把它落成代码、测试，或写进正式说明，再提交到 GitHub。

## 哪些内容不要直接进 GitHub

下面这些默认只留在本机，不作为仓库补充更新:

- `~/.codex/sessions/**`
- `~/.codex/shell_snapshots/**`
- `~/.codex/state_*.sqlite*`
- 仓库根目录里的 `.codex-skill-monitor-snapshot.txt`
- 原始终端输出、临时诊断脚本、一次性排查快照

这些文件属于运行痕迹，不是稳定资产。它们通常包含本地路径、工具状态、会话上下文，适合帮助复盘，但不适合直接当成 GitHub 内容。

## 手动复盘后的入库原则

当你做一次“本地运行自查”时，建议按这个顺序处理:

1. 先判断问题是不是已经通过代码和测试修掉
2. 如果已经修掉，就不再额外上传原始运行记录
3. 如果还没形成稳定规则，再把结论提炼进 README、runbook 或 roadmap
4. 只有在确实需要保留操作历史时，才更新 `skill-change-monitor.md`、`windows-translation-status.md`、`github-sync-status.md`

## 分支约定

- Mac / 通用 Python 主线同步: `codex/default-python-sync`
- Windows 专用补全线: `codex/windows-version-20260411`

## 运行顺序

1. 小时级监控先发现变化
2. 每天 22:00 汇总变化并转译 Windows 版本
3. 每天 00:00 在 Windows 和 Mac 版本都齐全时执行 GitHub 提交和推送
