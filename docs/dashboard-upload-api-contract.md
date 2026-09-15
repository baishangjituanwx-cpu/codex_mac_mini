# Dashboard Upload API Contract

这份文档定义的是 dashboard companion export 从本地仓库写入远端数据面板时，脚本实际依赖的 API contract。

## 适用范围

这份文档只描述“仓库脚本自动上传流”。

也就是：

- 设备本地运行 `dashboard-upload.js`
- 用管理员用户名和密码换取 `adminToken`
- 再把 companion export 写进目标 account group

它不描述下面这条流：

- 管理员在 `8081` 管理端生成一次性 `设备接入码`
- 新设备在 `8080` 页面通过 `新 Codex 设备接入` 完成设备绑定
- 浏览器端用绑定后的设备身份上传 JSON

所以：

- 如果你要接入“脚本自动上传设备”，看这份文档
- 如果你要接入“浏览器上传设备”，不要照着这份文档给管理员密码

## 配置入口

上传脚本是：

- [dashboard-upload.js](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/scripts/dashboard-upload.js>)

脚本不会再使用仓库内置默认地址或默认管理员账号。必须通过环境变量或命令行参数提供：

- `DASHBOARD_API_BASE`
- `DASHBOARD_ACCOUNT_NAME`
- `DASHBOARD_ADMIN_USERNAME`
- `DASHBOARD_ADMIN_PASSWORD`
- 可选：`DASHBOARD_WORKSPACE_NAME`

这些变量只给“脚本自动上传流”使用，不给浏览器设备绑定流使用。

## 调用顺序

固定顺序是 3 步：

1. 登录管理员接口
2. 查询 dashboard account index
3. 把 companion export 写入目标 account group

## 1. 管理员登录

- Method: `POST`
- Path: `/api/admin/login`
- Body:

```json
{
  "username": "your-admin-username",
  "password": "your-admin-password"
}
```

- Success response:

```json
{
  "adminToken": "..."
}
```

后续管理员接口都要带：

```http
X-Admin-Token: <adminToken>
```

## 2. 查询 account index

- Method: `GET`
- Path: `/api/dashboard/index`
- Headers:

```http
X-Admin-Token: <adminToken>
```

- Success response shape:

```json
{
  "accounts": [
    {
      "id": "acct_xxx",
      "name": "账号组名称",
      "workspaceName": "工作空间名称"
    }
  ]
}
```

脚本会按下面规则挑目标账号组：

- 必须匹配 `account.name === DASHBOARD_ACCOUNT_NAME`
- 如果设置了 `DASHBOARD_WORKSPACE_NAME`，还必须匹配 `workspaceName`
- 匹配 0 条：失败
- 匹配多条：失败，要求补 `workspaceName`

## 3. 上传 dashboard payload

- Method: `POST`
- Path: `/api/admin/accounts/:accountId/dashboard`
- Headers:

```http
Content-Type: application/json
X-Admin-Token: <adminToken>
```

- Request body:

```json
{
  "deviceToken": "admin-upload",
  "payload": {
    "meta": {},
    "board": {},
    "platforms": [],
    "footerLinks": []
  }
}
```

这里的 `payload` 必须已经通过：

- [docker-dashboard-contract.md](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/skill-center/skills/data-review/references/docker-dashboard-contract.md>)
- [validate-dashboard-export.js](</Users/baishangjituan/Documents/New project/github-ready/multi-platform-content-pipeline/scripts/validate-dashboard-export.js>)

- Success response:

```json
{
  "updatedAt": "2026-04-25T12:34:56.000Z",
  "sourceBatch": "dashboard-fixture",
  "mode": "admin"
}
```

脚本目前实际依赖的响应字段只有：

- `updatedAt`
- `sourceBatch`
- 可选 `mode`

## 本地写回产物

上传成功后，脚本还会在内容库里刷新：

- `dashboard-export/latest.json`
- `dashboard-export/latest.meta.json`

并由同步总控脚本再写：

- `dashboard-sync/latest-status.json`
- `dashboard-sync/latest-status.md`
- `dashboard-sync/history.jsonl`

## 失败语义

任何一步失败都必须阻断后续流程，不允许写“已同步成功”：

- 登录失败 -> `stage=upload`
- account 解析失败 -> `stage=upload`
- dashboard upload 失败 -> `stage=upload`
- JSON contract 不通过 -> `stage=validate`
- 导出仍是占位版 -> `stage=export`

## 多设备接入要求

别的 Codex 设备接入同一个 dashboard 时，必须保证：

1. 使用同一份 payload contract
2. 使用同一套上传接口顺序
3. 先跑 `dashboard-doctor.js`
4. 上传成功与否只看 `latest-status.json` 和远端 account group，不看口头描述

补充边界：

- 如果设备是浏览器上传设备，管理员应发一次性 `设备接入码` 或接入链接，而不是下发管理员凭证
- 只有要运行仓库脚本的设备，才需要 `DASHBOARD_ADMIN_USERNAME` 和 `DASHBOARD_ADMIN_PASSWORD`
