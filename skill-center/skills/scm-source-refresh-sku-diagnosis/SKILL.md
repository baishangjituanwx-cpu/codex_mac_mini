---
name: scm-source-refresh-sku-diagnosis
description: "只读诊断 SCM 阿里商品源刷新、异步消费和 SKU 可售状态；不自动修改库存、SKU 关联或代码。"
---

# SCM 商品源刷新与 SKU 可售诊断

适用于“全量更新结束但字段未落库”“库存有数但规格显示无货”等问题。默认只读；如需修复，必须另行取得明确授权并切换到受控变更流程。

## 诊断范围

- 阿里来源使用 source=6；后台刷新入口为 POST /sys/goods/goodsStore/batchSourceUpdate，它是异步受理，不代表每个商品字段已落库。
- 进度为 1（100%）应视为完成；只有进度小于 1 才是进行中。检查浏览器缓存或旧静态资源导致的误判。
- 对具体商品同时比较总库存、SKU 库存、规格关联和 available_sale。库存有数但 available_sale 为空、规格全部禁用时，记录为可售字段未生成/未写入，不直接判定为真实缺货。
- 检查异步消息消费、应用日志、磁盘空间和更新时间；区分“接口成功”“消息已消费”和“商品字段已落库”。

## 输出要求

按“观察事实→证据位置→最小结论→未确认原因→建议下一步”报告，包含时间戳和商品标识。不得把上游未返回、消费者跳过、同步写入失败三者之一臆断为唯一根因。

## 安全边界

- 默认不调用写接口、不改库存、不回写 SKU、不修改代码或缓存。
- 需要修复时先停止并请求明确的变更授权；不要在诊断 Skill 中夹带商品更新操作。
- 报告不得包含账号、密码、Cookie、Token、密钥、完整环境变量或私人资料。

## Windows Repo Mirror Notes

本技能是 SCM 浏览器控制型只读诊断，不需要独立的 PowerShell 或 `.cmd` 业务启动器。Windows 上复用 Codex 的共享浏览器网络检查和只读回读流程；不要把 `batchSourceUpdate` 改写为临时 PowerShell、`curl` 或本地写接口包装器，也不要绕过只读边界。

Windows 路径与快捷键规则：

- 技能安装位置通常为 `%USERPROFILE%\\.codex\\skills\\scm-source-refresh-sku-diagnosis\\`；
- 日志、截图、诊断报告和导出证据使用带引号的 `C:/Users/<name>/...` 绝对路径；共享资料使用带引号的 UNC 或映射盘路径；
- 浏览器 `press_key` 使用 `Control+R`/`F5`、`Control+L`、`Control+A`、`Alt+Left` 和 `Alt+Right`，不要照搬 Mac 的 `Meta` 键。

诊断结果必须区分接口受理、异步消费和字段落库三个状态；不要把 Cookie、Token、密钥、完整环境变量或原始请求头写入 Windows 文件、任务参数或环境变量。
