---
name: weixin-shop-paid-traffic-ops
description: Plan, operate after exact confirmation, and monitor WeChat Store paid traffic for 百亿好购店. Use for 商品托管, ROI and contribution-margin calculations, material upload/copy review, exact task readback, checkpoint logging, and post-campaign review.
---

# 微信小店投流与数据闭环

Use the official WeChat Store console with `chrome-devtools-mcp` for task and material operations. Use `lark-cli sheets` and `lark-cli docs` for the smallest exact cloud write followed by exact readback.

## Safety boundaries

- Default to read-only. A mutation requires the user's same-round confirmation of exact task ID, product ID, before/after value, and effective time.
- ROI, total budget, material, copy, switch, pause, and resume are separate mutations. Do not treat confirmation of one as approval for another.
- Before the final click, repeat the exact values and effective mode. After the click, re-read the official task detail/list and operation log.
- Ordinary promotion, institution promotion, alliance promotion, and marketing-center platform activities remain separate workflows.
- Never persist cookies, tokens, signatures, credentials, buyer privacy, plaintext phone numbers, or raw signed media URLs.
- Never report uploaded/reviewing material as approved, enabled, or delivering.

## Task execution card

- Store: `百亿好购店`
- Entry: `小店推广 -> 小店投放 -> 商品托管`
- Select by exact `platformGoodsId`; record exact `promotionId` after creation.
- The console uses one total daily budget for the task. Do not invent per-product budgets such as `15/9/6`.
- Treat creation minimum and later adjustment increment as different constraints. Read the current UI message every time; do not hard-code `50` or `55` as a universal rule.
- For an existing task, verify task status, switch, target ROI, total budget, balance, and modification time before and after any change.

## Cost-channel model

Every calculation must declare one mode:

- `PAID_TRAFFIC_ONLY`: paid-traffic attribution; exclude independent ordinary-promotion CPS commission.
- `CPS_ONLY`: ordinary/alliance CPS attribution; include the verified CPS commission and exclude paid-traffic spend.
- `STACKED_VERIFIED`: include both only when official evidence proves that the same attributed order actually bears both costs.

Do not double-count CPS by default.

```text
投流前贡献毛利 = 售价 * (1 - 平台费率 - 支付费率 - 售后准备金率)
                  - 实时成本 - 卖家运费 - 其它固定成本
贡献毛利率 = 投流前贡献毛利 / 售价
保本ROI = 1 / 贡献毛利率
目标ROI成交时单笔剩余贡献 = 投流前贡献毛利 - 售价 / 目标ROI
```

For task `17650521` and product `10001252850579`, the verified `PAID_TRAFFIC_ONLY` inputs are price `19.90`, cost `5.63`, seller freight `2.00`, platform fee `2%`, payment fee `0.6%`, after-sale reserve `3%`, and fixed cost `0.50`. They produce contribution margin `10.6556`, margin rate about `53.55%`, and break-even ROI about `1.8676`. At target ROI `2.30`, estimated remaining contribution per attributed order is about `2.0034`.

## Material and copy flow

- Read the live `添加素材` page before upload. Verified current compatibility is video duration `5-300` seconds, MP4, H.264/AAC-compatible streams, file below `500 MB`; the actual page response remains authoritative.
- Record exact material ID, filename, source, upload time, review status, spend, exposure, clicks, orders, and GMV.
- `配置投放文案` is per material. Read the live character rule, use only verified product facts, and avoid unverified price, discount, stock, sales, certification, medical, or absolute claims.
- Copy modification can trigger re-review and temporarily stop that material. Record the operation-log time and keep status `MATERIAL_REVIEWING` until official approval appears.
- See `references/paid-traffic-material-qa.md` for media QA and copy gates.

## Checkpoints and decisions

Classify each checkpoint as `MATERIAL_REVIEWING`, `COLD_START_WAITING`, `NO_EXPOSURE_AFTER_WAIT`, `DELIVERY_ACTIVE`, or `PAUSE_RECOMMENDED`.

- Exposure `>0` with spend `0`: observe; do not judge ROI.
- Exposure `0`: verify material review, task switch, delivery eligibility, and restrictions before proposing new material or bid changes.
- Spend with no paid order: compare cumulative spend with the confirmed affordable CPA and propose action; do not pause automatically.
- Paid orders with actual ROI below break-even: propose pause.
- Actual ROI between break-even and target: keep budget unchanged.
- Actual ROI at or above target with positive contribution: observe before scaling.

The daily first checkpoint after `20:30` is read-only unless the user separately confirms a mutation.
If no eligible live capture exists, use `LATEST_VERIFIED_EVIDENCE_ONLY`.

## Required evidence

Read task/product IDs, task status/switch, target ROI, total budget, balance, modification time, material IDs/status/copy, exposure, spend, clicks, add-to-cart, orders, paid orders, GMV, attributed GMV, actual成交ROI,成交成本, checkpoint time, and official operation log. Derived spreadsheet fields use formulas; raw values are never estimated.

See `references/data-contract.md` for the cloud field contract.

## Completion labels

- `MATERIAL_REVIEWING`
- `COLD_START_WAITING`
- `NO_EXPOSURE_AFTER_WAIT`
- `DELIVERY_ACTIVE`
- `PAUSE_RECOMMENDED`
- `LATEST_VERIFIED_EVIDENCE_ONLY`

## Windows Repo Mirror Notes

Keep this workflow shared across platforms. On Windows use quoted paths and `Control+R`, `Control+L`, `Control+A`, `Alt+Left`, and `Alt+Right` for browser keyboard actions. Do not fork the business rules into a separate PowerShell implementation.
