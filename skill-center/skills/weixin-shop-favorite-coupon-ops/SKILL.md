---
name: weixin-shop-favorite-coupon-ops
description: 通过 chrome-devtools-mcp 读取并安全规划微信小店“店铺收藏券”，计算全店适用范围、单笔和整批极端亏损，获得同轮精确确认后创建并回读验证。用户提到店铺收藏券、收藏有礼、全店优惠券或要求评估/创建收藏券时使用。
---

# 微信小店店铺收藏券

## 核心边界

- 使用 `chrome-devtools-mcp` 操作微信小店官方后台；先刷新首页和优惠券页面，再读取实时表单规则与当前草稿/已创建券。
- 默认只读。创建、发布、启用、修改、删除或停用优惠券都属于写入；必须在同一轮展示精确优惠方式、面额、门槛、适用范围、券量、领取时间、使用时间和预计生效时间，并取得用户确认后才点击最终提交。
- 不保存或输出 Cookie、token、magic 值、请求签名、登录凭据、买家隐私或明文手机号；不输出原始带签名媒体 URL。
- “店铺收藏券”与普通推广、机构推广、联盟活动、营销中心平台活动分开记录，不得混淆。

## 读取流程

1. 打开 `https://store.weixin.qq.com/shop/home`，确认当前店铺和登录上下文。
2. 进入“营销工具 -> 店铺收藏券 -> 去配置”，刷新页面，读取实时可选优惠方式、面额/折扣、使用门槛、券量、每人限领、领取时间、使用时间、适用范围和可排除商品设置。
3. 读取微信小店“销售中”全部分页，校验页面总数、各页返回行数之和、唯一 `platformGoodsId` 三者一致；逐商品记录实时售价、库存、销售状态和平台 SKU 映射。
4. 用慧策 HTTP API 读取对应当前分销商品、商品详情和 SKU：`supplierGoodsId -> itemId -> distributorGoodsId -> publishId -> platformGoodsId -> platformSkuId`。读取实时分销成本、`controlMinPrice`、卖家承担运费、售后地址来源和商品供销状态。慧策证书错误时仅按既有安全方式使用 `HUICE_TLS_INSECURE=1`。
5. 任一当前价格、库存、成本、费用、最低限价、售后地址或映射未知时，列为“不可安全纳入”，不得用历史值或 `suggestedPrice` 猜测补齐。

## 风险计算

对每个 SKU 使用未提前四舍五入的中间值。默认投流外订单贡献模型为：

```text
优惠前贡献 = 售价 * (1 - 平台费率 - 支付费率 - 售后准备金率)
             - 实时分销成本 - 卖家运费 - 其它固定成本
优惠后贡献 = 优惠前贡献 - 实际优惠金额
券导致的单笔额外亏损 = max(0, -优惠后贡献) - max(0, -优惠前贡献)
```

对满减/立减券取实际订单可用的最大优惠金额；折扣券按当前售价和平台规则计算最大优惠。整批极端风险至少报告：

```text
最大名义优惠支出 = 实际可核销券数 * 单张最大优惠
最大额外亏损 = 实际可核销券数 * max(各适用 SKU 的单笔额外亏损)
最大优惠后订单亏损 = 实际可核销券数 * max(各适用 SKU 的 max(0, -优惠后贡献))
```

同时给出最坏商品、商品 ID、SKU、售价、成本、运费、全部费率、优惠前贡献和优惠后贡献。若券量、门槛或核销规则未知，输出区间和阻断原因，不得声称精确上限。

## 安全决策

- “全店商品”只有在所有实际可售 SKU 都能通过当前成本、最低限价、地址和毛利复核时才可作为安全范围；不能把库存 0、停供、风险隔离、地址缺失或映射缺失商品当作有效可售商品。
- 任何 SKU 使用券后贡献为负时，不直接创建全店券。优先提出使用门槛、降低面额、限制券量或排除具体商品，并重新计算。
- `controlMinPrice` 高于当前售价时，先记录价格风险；优惠券流程不得用优惠券掩盖低价风险，也不得自动改价。
- 创建前再次读取实时商品数、售价、库存、费用和券配置；最终确认文本必须逐项列出精确值。
- 提交后立即读取优惠券列表/详情和操作结果，核对状态、适用范围、券量、时间和面额；任何字段不一致都标记未完成。

## 输出与留痕

- 业务描述优先使用中文；仅保留接口字段、ID 和机器判定码的原文。
- 生成脱敏风险报告，至少包含读取时间、店铺、商品总数校验、候选配置、逐 SKU 风险分类、最大名义支出、最大额外亏损、未纳入原因和是否需要用户确认。
- 未得到精确确认时，明确写“仅完成读取和模拟，未创建或发布优惠券”。

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher for its browser-controlled work. The Windows-usable equivalent is the same Codex `chrome-devtools-mcp` workflow, so keep the browser behavior shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back and forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-favorite-coupon-ops\\`. Keep screenshots, structured risk reports, exported logs, and copied attachments quoted and in `C:/Users/<name>/...` form instead of `/Users/...`; use quoted UNC or mapped-drive paths when reading the shared Huice client, for example `\\\\BSJT168\\BSJT 共享给我\\AI专用\\[Codex]Mac部署\\旺店通\\huice-goods-analysis`.

When the shared Huice client reports the documented certificate error, set the opt-in fallback only for the current PowerShell session and clear it afterward:

```powershell
$env:HUICE_TLS_INSECURE = "1"
try {
  # Run the existing shared Huice/Node workflow; do not replace it with curl or a .cmd wrapper.
}
finally {
  Remove-Item Env:HUICE_TLS_INSECURE -ErrorAction SilentlyContinue
}
```

Do not use `setx`, save the variable in the Windows profile, or enable the fallback by default. Never save cookies, tokens, signed URLs, credentials, or raw request headers in Windows evidence files.
