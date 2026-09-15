# 数据复盘固定模板

每次复盘都使用下面这套中文结构。

```md
# {exact-review-date} {batch-or-topic} 多平台数据复盘

## 1. 复盘范围
- 复盘批次：
- 复盘主题：
- 计划平台：
- 计划格式：
- 对照窗口：
- 已核验材料：

## 2. 总览
- 图文最稳：
- 短视频当前最稳：
- 当前最大阻塞：
- 当前最容易被误判的平台：
- 本轮总判断：
- Keep：
- Cut：
- Retest：

## 3. 分平台详细状态
### {platform}
- 核验等级：
- 核验页面：
- 计划内容：
- 当前作品：
- 发布状态：
- 当前可见数据：
- 账号盘面：
- 近几条对照：
- 最强信号：
- 最大问题：
- 高价值评论 / 私信：
- 诊断：
- 明日动作：
- 决策：Keep / Cut / Retest

### {next-platform}
- 核验等级：
- 核验页面：
- 计划内容：
- 当前作品：
- 发布状态：
- 当前可见数据：
- 账号盘面：
- 近几条对照：
- 最强信号：
- 最大问题：
- 高价值评论 / 私信：
- 诊断：
- 明日动作：
- 决策：Keep / Cut / Retest

## 4. 跨平台结论
- 图文侧结论：
- 短视频侧结论：
- 标题 / 封面结论：
- 账号 / 审核 / 路由结论：
- 本轮最不该误判的点：

## 5. 下一批图文内容高占比倾向
- 高占比主母题：
- 高占比主判断：
- 标题优先顺序：
- 正文结构模板：
- 必须保留的具体例子：
- 需要避开的写法：
- 平台倾向：

## 6. 下一批小云雀视频高占比倾向
- 主题文案优先：
- 高占比核心母题：
- 高占比核心判断：
- 开头高占比规则：
- 这轮应避开的短视频表达：
- 可直接用于下一轮的小云雀提示词骨架：

## 7. 未完成核验项
- 平台：
- 缺少什么：
- 下一步补什么：

## 8. 写回规则
- 需要写回 skill / memory 的经验：
- 明天必须复查的点：
- 账号趋势要继续观察的平台：

## 9. Docker 看板数据映射（晚间复盘自动化 / 需更新 8 平台 Docker 看板时必填）
- 推荐直接给一个 `json` 代码块；如果流程需要文件交接，也可以把同一对象写成 companion JSON 文件
- 如果用了 companion JSON 文件，在这里明确写一行：`- companion JSON 文件：/absolute/path/to/export.json`
- 如果这是当前工作区的晚间复盘自动化，再额外写明：
  - `- contract 校验结果：`
  - `- latest.json 路径：/absolute/path/to/latest.json`
  - `- 目标账号组：`
  - `- 数据面板同步状态：已上传 / 上传失败待补`
  - `- 同步审计日志：/absolute/path/to/content-library/logs/review/dashboard-sync/latest-status.md`
- 首次在新设备接入时，先配置仓库根目录 `.env.dashboard` 或 `.env.dashboard.local`
- 这一步优先使用仓库脚本：`node scripts/dashboard-sync-review.js --review-date YYYY-MM-DD`
- `board.title`：
- `board.dateLabel`：
- `board.subtitle`：
- `board.northStar`：
- `board.summary`：必须正好 4 项；每项都写 `label / value / note / tone`
- `board.keep`：必须正好 3 项
- `board.cut`：必须正好 3 项
- `board.next`：必须正好 3 项
- `platforms`：必须正好 8 项，并覆盖 `快手 / 视频号 / 微博 / 头条号 / 百家号 / 抖音 / B站 / 知乎`
- 每个平台卡片都必须写出：
  - `key`
  - `name`
  - `status`
  - `statusLabel`
  - `latestTitle`
  - `publishTime`
  - `contentType`
  - `primaryLabel`
  - `primaryValue`
  - `compareLabel`
  - `baselineValue`
  - `baselineNote`
  - `windows`：固定 `今日 / 近7日账号 / 近30日账号`
  - `metrics`：正好 4 项
  - `diagnosis`
  - `action`
- `primaryValue` 必须保持数值型，缺失时写 `0`，不要写 `—`
- `footerLinks`：只有在真实文件存在时才补
```

## 模板规则

- 如果某个平台是重复跳过、审核中、被阻塞或没找到，也必须单独写出，不允许直接省略。
- 如果后台只核到了公开页或入口页，必须明确写 `公开页已核验` 或 `未完成内容级核验`。
- 如果数据缺失，写 `暂未可见`，不要把它偷换成失败。
- 保留平台后台原始状态词，比如 `已发布`、`已推荐`、`首发`、`审核中`。
- 复盘中必须写绝对日期，不用“今天”“昨天”代替。
- 当用户要求趋势复盘、最近几条对比或账号维度时，`账号盘面` 和 `近几条对照` 两项是强制项。
- 飞书同步稿必须基于这份结构压缩，且只允许中文输出。
- 如果本次复盘要更新 Docker 看板，或任务本身就是当前工作区的晚间复盘自动化，`## 9. Docker 看板数据映射` 是强制项，并且要遵守 [docker-dashboard-contract.md](./docker-dashboard-contract.md)。
