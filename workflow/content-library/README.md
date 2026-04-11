# Content Library

这个目录是整套流程的运营数据层。

## 目录说明

- `assets/`
  - 实际视频、封面、字幕、截图
  - 默认不建议把大体积生成素材直接提交到 GitHub
- `posts/`
  - 每次 campaign 的内容包
- `logs/`
  - 每个平台发布后的回填日志
- `templates/`
  - 新 campaign 的模板源
- `examples/`
  - 本地已跑通案例

## 推荐流程

1. 先执行 `scripts/init_campaign.js`
2. 先填 `posts/shared/`
3. 再填 `posts/video/` 和各平台分包
4. 发布后立即回填 `logs/`
5. 复盘时同时看 `posts/ + logs/`

## 资产路径约定

统一使用:

```text
{{WORKSPACE_ROOT}}/workflow/content-library/assets/generated/<campaign-id>/
```

这里的 `{{WORKSPACE_ROOT}}` 只是占位符，表示仓库根目录。

## 为什么这里不用数据库

因为当前阶段最重要的是:

- 可读
- 可 diff
- 可复制
- 可直接给 Codex 当上下文

Markdown 在这一阶段比单独建数据库更适合。

