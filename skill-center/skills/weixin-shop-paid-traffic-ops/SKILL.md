---
name: weixin-shop-paid-traffic-ops
description: Plan and monitor manual WeChat Store paid traffic for 百亿好购店. Use for 商品托管 task planning, ROI and contribution-margin calculations, exact task/product readback, checkpoint logging, and post-campaign review. Never submit or mutate a paid-traffic task on the user's behalf.
---

# 微信小店手动投流与数据闭环

Cloud and official-readback workflow for manual paid traffic. The operator performs the final click in the WeChat Store console.

## Boundaries

- Use official WeChat Store traffic pages and `chrome-devtools-mcp` for exact task/product readback.
- Use `lark-cli sheets` and `lark-cli docs`; write the smallest exact range and read it back.
- Never automatically change ROI, budget, material, switch, pause, resume, or submit a new托管 task.
- Never persist cookies, tokens, signatures, credentials, buyer privacy, plaintext phone numbers, or raw signed media URLs.

## Manual execution card

- Store: `百亿好购店`
- Entry: `小店推广 -> 小店投放 -> 商品托管`
- Select by exact `platformGoodsId`.
- The operator enters one product ID, one target ROI, and one total daily budget.
- The current console minimum total daily budget is `50`; do not enter per-product budgets such as `15/9/6`.
- The operator performs the final `立即托管商品` click and records task ID, status, and time.

Before clicking, compare exact product name, price, stock, ROI, budget, and address/eligibility evidence. Any mismatch stops the operation.

## ROI and state rules

```text
投流前贡献毛利 = 售价 * (1 - 平台费率 - 支付费率 - 普通佣金率 - 售后准备金率)
                  - 实时成本 - 卖家运费 - 其它固定成本
贡献毛利率 = 投流前贡献毛利 / 售价
保本ROI = 1 / 贡献毛利率
目标ROI = 保本ROI * 1.30
```

For `10001252850579`, verified inputs produce contribution margin `8.6656`, margin rate `43.55%`, break-even ROI about `2.30`, and starting target ROI `2.99`. This is a planning target, not a guaranteed delivery result.

Classify each checkpoint as `MATERIAL_REVIEWING`, `COLD_START_WAITING`, `NO_EXPOSURE_AFTER_WAIT`, `DELIVERY_ACTIVE`, or `PAUSE_RECOMMENDED`. The 20:30 checkpoint is read-only; missing same-session evidence remains `LATEST_VERIFIED_EVIDENCE_ONLY`.

## Required fields

Read task ID, product ID, material status, task status/switch, target ROI, total budget, balance, modification time, exposure, spend, clicks, add-to-cart, orders, paid orders, GMV, attributed GMV, actual成交ROI,成交成本, and checkpoint time. Derived spreadsheet fields must use formulas; official raw values cannot be estimated.

See `references/data-contract.md` for the sheet field contract.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` business wrapper. The Windows-usable equivalent is the same official WeChat Store console flow plus the shared `lark-cli sheets` and `lark-cli docs` commands, so keep the workflow shared rather than forking task creation or checkpoint logging by platform.

When a browser verification step needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-paid-traffic-ops\\`. Any local evidence export, screenshot path, or checkpoint backup should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`.

When invoking the shared cloud-write helpers from PowerShell, keep sheet names, task IDs, exact ranges, and document keywords quoted so they remain text:

```powershell
lark-cli sheets write-range `
  --sheet "小店投放数据" `
  --range "A2:Z2" `
  --values-file "C:/Users/<name>/Downloads/paid-traffic-checkpoint.json"
```
