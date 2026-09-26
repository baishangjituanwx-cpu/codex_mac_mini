---
name: scm-single-product-select
description: "在 SCM 商品详情页完成单个商品的选品，并核验 SKU 可选状态和已选数量；不替代批量选品或商品源刷新。"
---

# SCM 单商品选品

适用于用户指定一个商品、需要从详情页加入选品的场景。执行前必须有明确商品标识和用户授权。

## 执行流程

1. 打开目标商品详情，核对商品名称、来源和商品标识，避免在搜索结果相似项上操作。
2. 检查颜色、尺码或其他规格是否可选。若全部规格灰显、页面显示“无货”或 available_sale 为空，停止加入动作，转交 scm-source-refresh-sku-diagnosis 做只读诊断。
3. 在规格可选且用户确认后点击“加入选品”，等待成功提示。
4. 打开“已选商品”，核对数量是否按预期增加（例如 0→1），并记录商品是否可见。

## 边界

- “加入选品”是商户选品写入；不要把它与后台 batchSourceUpdate 商品源刷新混为一谈。
- 不通过修改库存、前端状态或接口参数强行启用灰显规格。
- 失败时记录页面状态、接口字段和成功回执；不输出凭据或会话信息。

## Windows Repo Mirror Notes

本技能是 SCM 浏览器控制流程，不需要独立的 PowerShell 或 `.cmd` 业务启动器。Windows 上复用 Codex 的共享浏览器控制能力、同一商品详情回读和 SKU 状态核验规则，不要用临时 PowerShell、`curl` 或本地 API 包装器绕过页面证据。

Windows 路径与快捷键规则：

- 技能安装位置通常为 `%USERPROFILE%\\.codex\\skills\\scm-single-product-select\\`；
- 截图、商品证据和导出记录使用带引号的 `C:/Users/<name>/...` 绝对路径；共享资料使用带引号的 UNC 或映射盘路径；
- 浏览器 `press_key` 使用 `Control+R`/`F5`、`Control+L`、`Control+A`、`Alt+Left` 和 `Alt+Right`，不要照搬 Mac 的 `Meta` 键。

加入选品仍需当前会话中的明确商品标识和用户授权；不要把 Cookie、Token、密钥或原始请求头写入 Windows 文件、任务参数或环境变量。
