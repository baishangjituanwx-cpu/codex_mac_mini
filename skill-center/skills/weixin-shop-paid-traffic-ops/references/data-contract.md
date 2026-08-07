# 投流数据契约

`小店投放数据` uses one row per exact task, product, date, and checkpoint. Later checkpoints append a row and do not overwrite earlier evidence.

Raw fields include task/product IDs, status, material review, switch, target ROI, total budget, balance, modification time, cold-start stage, checkpoint, exposure, spend, clicks, add-to-cart, orders, paid orders, GMV, attributed GMV, actual成交ROI,成交成本, and evidence source.

```text
CTR = 点击 / 曝光
CPC = 消耗 / 点击
ROAS = 归因GMV / 消耗
CPA = 消耗 / 支付订单
投流后贡献毛利 = 归因GMV * 投流前贡献毛利率 - 消耗
净ROI = 投流后贡献毛利 / 消耗
```

Blank denominators remain blank. Use zero only when the official source explicitly reports zero.
