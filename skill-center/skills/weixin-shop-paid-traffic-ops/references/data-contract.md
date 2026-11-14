# 投流数据契约

`小店投放数据` uses one row per exact task, product, date, and checkpoint. Later checkpoints append rows and never overwrite earlier raw evidence.

## Raw fields

- Task/product: task ID, product ID, product name, actual price, actual stock, task status, switch.
- Delivery: target ROI, total budget, balance, modification time, exposure, spend, clicks, add-to-cart, orders, paid orders, GMV, attributed GMV, actual成交ROI,成交成本.
- Material: material IDs, filenames, type, source, review status, configured copy, copy operation-log time, material-level delivery metrics.
- Audit: checkpoint time/type, cold-start stage, evidence source, prior ROI/budget, effective mode, mutation evidence.
- Cost channel: `PAID_TRAFFIC_ONLY`, `CPS_ONLY`, or `STACKED_VERIFIED`; record whether CPS commission is included.

Historical observations remain immutable. A corrected calculation convention is appended as `口径版本/修正说明`; it does not rewrite official raw values.

## Derived fields

```text
CTR = 点击 / 曝光
CPC = 消耗 / 点击
ROAS = 归因GMV / 消耗
CPA = 消耗 / 支付订单
投流后贡献毛利 = 归因GMV * 投流前贡献毛利率 - 消耗
净ROI = 投流后贡献毛利 / 消耗
```

For `PAID_TRAFFIC_ONLY`, independent ordinary-promotion CPS commission is excluded. Include it only for `CPS_ONLY` or evidence-backed `STACKED_VERIFIED` orders. Blank denominators remain blank; use zero only when the official source explicitly reports zero.
