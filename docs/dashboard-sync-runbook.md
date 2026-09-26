# Dashboard Sync Runbook

这套脚本把晚间复盘的 Docker 看板同步收口成同一条链路，适合其他 Codex 设备直接接入。

## 先分清两条接入流

当前工作区里，“新设备接入 dashboard”和“脚本自动上传 dashboard”不是一回事。

### A. 浏览器设备绑定流

适用场景：

- 新 Codex 设备只需要在 `8080` 页面里上传复盘 JSON
- 设备操作者不运行仓库内脚本
- 设备操作者不应持有管理员用户名和密码

正确流程：

1. 管理员打开 `8081` 管理端并登录
2. 进入目标工作账号和目标账号组
3. 生成一次性 `设备接入码` 或 `接入链接`
4. 把接入码或接入链接发给新设备操作者
5. 新设备操作者打开 `8080`
6. 走 `新 Codex 设备接入 -> 使用接入码绑定设备`
7. 绑定成功后，这台设备只对对应账号组拥有上传权限

这一条流：

- 不使用 `工作账号登录`
- 不要求 `.env.dashboard`
- 不要求管理员凭证落到设备本地

### B. 仓库脚本自动上传流

适用场景：

- 设备要运行 `dashboard-sync-review.js`
- 设备要从本地复盘 Markdown 自动导出 companion JSON 并直接写远端 account group
- 设备需要跑 `dashboard-doctor -> export -> validate -> upload` 整条链

这一条流才需要下面的 `.env.dashboard` 配置和管理员凭证。

## 入口

- 预检: `node scripts/dashboard-doctor.js --review-date YYYY-MM-DD`
- 导出 companion JSON: `node scripts/dashboard-export-review.js --review-date YYYY-MM-DD`
- contract 校验: `node scripts/validate-dashboard-export.js --file /absolute/path/to/export.json`
- 一键闭环: `node scripts/dashboard-sync-review.js --review-date YYYY-MM-DD`
- macOS / Linux 包装器: `bash scripts/dashboard-sync.sh --review-date YYYY-MM-DD`
- Windows PowerShell 包装器: `.\scripts\dashboard-sync.ps1 --review-date YYYY-MM-DD`

优先使用一键闭环命令。它会依次完成:

1. 从复盘正文 `## 3. 分平台详细状态` 生成真实 platform cards
2. 校验 JSON contract
3. 刷新 `dashboard-export/latest.json`
4. 上传到远端 dashboard account group
5. 写入固定同步审计文件

## 环境准备

Node.js 18+ 是必需项，因为 `dashboard-upload.js` 使用了原生 `fetch`。

仓库默认会自动寻找两种内容库布局:

- `workflow/content-library`
- `content-library`

如果你的设备不是这两种布局，在仓库根目录创建 `.env.dashboard` 或 `.env.dashboard.local`，并设置:

```dotenv
CONTENT_LIBRARY_ROOT=workflow/content-library
```

如果设备走的是“仓库脚本自动上传流”，同一个文件里还需要配置 dashboard 上传目标：

```dotenv
DASHBOARD_API_BASE=http://your-dashboard-host:8080
DASHBOARD_ACCOUNT_NAME=your-account-group
DASHBOARD_WORKSPACE_NAME=your-workspace-name
DASHBOARD_ADMIN_USERNAME=your-admin-username
DASHBOARD_ADMIN_PASSWORD=your-admin-password
```

参考模板在 [`.env.dashboard.example`](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/.env.dashboard.example>)。

建议首次接入按这个顺序跑:

1. `node scripts/dashboard-doctor.js --review-date YYYY-MM-DD`
2. `bash scripts/dashboard-sync.sh --review-date YYYY-MM-DD`
3. 或 Windows 下 `.\scripts\dashboard-sync.ps1 --review-date YYYY-MM-DD`

如果设备走的是“浏览器设备绑定流”，不要先配 `.env.dashboard`。先让管理员在 `8081` 里发一次性接入码，再在 `8080` 里绑定设备。

## 必要输入

- 一份按固定模板写好的复盘文件
- 复盘文件中必须包含 `## 3. 分平台详细状态`
- 如果要上传 dashboard，复盘中必须补 `## 9. Docker 看板数据映射`
- 运行设备必须能访问远端 dashboard API

## 产物

运行 `dashboard-sync-review.js` 后，会写入:

- companion export:
  `workflow/content-library/logs/review/dashboard-export/<batch>-dashboard-export.json`
- latest 指针:
  `workflow/content-library/logs/review/dashboard-export/latest.json`
- latest meta:
  `workflow/content-library/logs/review/dashboard-export/latest.meta.json`
- 同步审计:
  `workflow/content-library/logs/review/dashboard-sync/latest-status.json`
  `workflow/content-library/logs/review/dashboard-sync/latest-status.md`
  `workflow/content-library/logs/review/dashboard-sync/history.jsonl`

如果当前工作区使用顶层 `content-library/` 布局，路径会自动切换到对应目录。

## 失败边界

- 如果导出结果仍是 `local-package-review-export` 这类占位模式，脚本会直接失败
- 如果 contract 不通过，不会继续上传
- 如果远端 dashboard 账号组上传失败，会在同步审计文件里记录失败阶段和错误文本
- `latest-status.json` 才是最终成功与否的准信号，不要只看终端输出

## 只导出不上传

如果当前设备只是要生成 companion JSON，不要直接跑上传链。

用这两步：

```bash
node scripts/dashboard-export-review.js --review-date YYYY-MM-DD
node scripts/validate-dashboard-export.js --file /absolute/path/to/export.json
```

这种模式适合：

- 本地先检查复盘字段有没有被正确抽出来
- 在测试环境确认 export 长相
- 不希望把测试数据写进远端 dashboard

只有确定要写远端 account group 时，才跑：

```bash
node scripts/dashboard-sync-review.js --review-date YYYY-MM-DD
```

## 多设备写入规则

多台 Codex 设备接入同一个 dashboard 时，按这 4 条执行：

1. 同一天同一批次，只允许一个设备负责最终上传
2. 如果只是辅助检查或字段修正，只跑导出和校验，不直接上传
3. `latest.json` 和 `latest.meta.json` 只代表最后一次成功上传，不代表历史全貌
4. 冲突排查先看：
   - `dashboard-sync/history.jsonl`
   - `dashboard-sync/latest-status.json`
   - 远端 account group 当前显示的 `sourceBatch`

如果两台设备都要处理同一天数据，先约定唯一的 `sourceBatch` 负责人，否则最后一次上传会覆盖前一次的 latest 指针。

## 哪些文件不入库

下面这些属于运行产物或本地配置，不应该提交到 GitHub：

- `.env.dashboard`
- `.env.dashboard.local`
- `workflow/content-library/logs/review/dashboard-export/latest.json`
- `workflow/content-library/logs/review/dashboard-export/latest.meta.json`
- `workflow/content-library/logs/review/dashboard-sync/latest-status.json`
- `workflow/content-library/logs/review/dashboard-sync/latest-status.md`
- `workflow/content-library/logs/review/dashboard-sync/history.jsonl`

如果你的工作区使用顶层 `content-library/` 布局，同样规则适用到对应目录。

## 多设备接入

其他 Codex 设备接入时，最少要做到这 4 点:

1. 仓库根目录存在这套 `scripts/`
2. 本机内容库布局能被脚本解析到
3. 如果设备要跑脚本自动上传，`.env.dashboard` 填入该设备自己的 dashboard API 和管理员凭证
4. 如果设备只走浏览器上传，改用管理员发放的一次性 `设备接入码`，不要把管理员凭证下发到该设备
5. 复盘文件严格遵守 `data-review` 模板，不省略 8 平台卡片
