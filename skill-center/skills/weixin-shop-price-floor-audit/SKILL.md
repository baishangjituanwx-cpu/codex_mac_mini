---
name: weixin-shop-price-floor-audit
description: Audit and remediate WeChat Store product price floors, margins, supplier status changes, distribution-cost or freight changes, stopped supply, SKU mappings, goods_detail after-sale addresses, live price and inventory, and publish failures. Use for 慧策供销商分销状态变动、分销价格变动、最低限价/controlMinPrice、破价、成本上涨、停供下架、库存归零、平台售价调整、全量在售审计、铺货前复核、推广前毛利复核, or any request to verify that WeChat products remain sellable and profitable.
---

# 微信小店限价与供销审计

对微信小店商品执行逐 SKU 的当前状态审计。慧策事件日志只用于生成候选；最终结论必须来自实时商品详情、精确映射、当前刊登记录和微信官方精确商品回查。

## Tool Boundaries

- Use the Huice shared HTTP client and scripts for all Huice reads and writes. Do not click Huice business buttons.
- Use `chrome-devtools-mcp` on Huice only to confirm the authenticated host, refresh ephemeral authentication, or learn the current request contract.
- Use `chrome-devtools-mcp` on the official WeChat backend for exact product/SKU readback and an authorized emergency delist or price edit.
- Use `weixin-shop-goods-inspection` for official product-list extraction and exact status verification.
- Use `lark-cli sheets` and `lark-cli docs` for cloud records. Write, then read the exact range or section back.
- Use `huice-distribution-order-push` for outsourced-order push work; do not mix order states into product publication states.
- Never save or output cookies, tokens, request signatures, passwords, buyer privacy, or plaintext phone numbers.

The shared HTTP reference is:

```text
/Volumes/BSJT 共享给我/AI专用/[Codex]Mac部署/旺店通/huice-goods-analysis
```

Read `docs/weixin-price-floor-and-supplier-change-audit-20260802.md` when an endpoint or historical example is needed.

## Non-Negotiable Gates

1. Treat supplier SKU `controlMinPrice` as P0. Never substitute `suggestedPrice`.
2. Accept an after-sale address only from live `goods_detail`, with complete recipient, phone, province/city/district, and detail.
3. Establish the exact chain before any action:

```text
supplierGoodsId
-> itemId
-> distributorGoodsId
-> publishId
-> merchantCode / outerId
-> platformGoodsId
-> platformSkuId
```

4. Recompute every SKU from current distribution cost and seller-paid freight. Do not reuse a historical margin.
5. Require after a 10% ordinary promotion: profit amount > 0 and profit margin > 2%.
6. Require without promotion: safety margin >= 8%.
7. Count a product as selling/hard-success only after Huice current publication evidence and exact official WeChat product evidence agree.
8. Treat request acceptance, save success, task creation, draft, review, stale task rows, and old success rows as non-final.
9. A cloud-ledger write failure or missing required field means the workflow is incomplete.

## Price Calculation

For each SKU, use current values:

```text
P   = actual or proposed selling price
C   = current distribution cost
F   = seller-paid freight
O   = other fixed cost
rp  = current platform fee rate
rq  = current payment fee rate
rr  = current after-sale reserve rate
rc  = current promotion/activity commission rate
```

Calculate without intermediate rounding:

```text
promotionProfit = P * (1 - rp - rq - rr - rc) - C - F - O
promotionMargin = promotionProfit / P
safetyProfit    = P * (1 - rp - rq - rr) - C - F - O
safetyMargin    = safetyProfit / P
```

Use the current validated rates from the platform and business rules. If any fee is unknown, stop at `MISSING_COST_COMPONENT`; never assume zero.

Determine the target price:

```text
targetPrice = roundUpToAllowedIncrement(
  max(controlMinPrice, promotionMarginFloorPrice, safetyMarginFloorPrice, businessBandFloor)
)
```

After rounding, recompute both margins. The promotion threshold is strict: exactly 2% is not sufficient.

## Audit Workflow

### 1. Read current change candidates

1. Read the Huice change count.
2. Read both current tabs: price changes and supplier-status changes.
3. Deduplicate by supplier product and preserve all affected `itemId` values.
4. Report event-row counts separately from current affected-product counts.

Never say that 58 event rows mean 58 currently stopped products. Re-read current state.

### 2. Build exact current facts

For every affected SKU, read:

- current supplier sale/supply state
- live `distributionPrice`
- seller-paid freight and any fixed costs
- `controlMinPrice`
- current stock
- complete `goods_detail` address
- distributor product and SKU IDs
- publication ID, merchant code, platform product ID and platform SKU ID
- current WeChat selling state, actual price and actual stock
- current ordinary-promotion commission and activity obligations, if any

If a source only has a title or a partial ID, classify it as `MAPPING_INCOMPLETE` and do not act.

### 3. Run the P0 checks

Run the floor and margin checks at all of these checkpoints:

- candidate selection
- after joining distribution
- before publish save
- before publish submit
- after official selling success
- before promotion or platform-activity creation
- before and after any price change
- every supplier-change audit

### 4. Classify and act

| Classification | Required behavior |
| --- | --- |
| `COMPLIANT` | Record and leave unchanged |
| `SUPPLIER_STOPPED_LIVE` | Stop sale first, set Huice publication SKU stock to 0, then exact-read both systems |
| `BELOW_CONTROL_MIN_PRICE` | Stop unsafe sale immediately; calculate and publish a compliant price only after all gates pass |
| `MARGIN_FAIL` | Raise to the calculated target; if the allowed price band cannot pass, set stock to 0 and delist |
| `ADDRESS_INCOMPLETE` | Delist or keep unpublished; do not republish until live `goods_detail` is complete |
| `MAPPING_INCOMPLETE` | Record only; repair the mapping without creating a duplicate product |
| `REPAIRABLE_PUBLISH_FAILURE` | Repair the exact platform failure field, re-read every gate, then resubmit once |
| `SUPPLY_RECOVERED` | Record and review; never auto-list or auto-lower price |
| `COST_DECREASED` | Record and review; never auto-lower price |

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher for its browser-controlled work. The Windows-usable equivalent is the same Codex workflow: keep Chrome DevTools MCP for WeChat readback and use the shared Huice HTTP client/scripts rather than forking wrapper scripts in this repo.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-price-floor-audit\\`. Any local evidence path, exported audit path, or copied attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`.

When the Huice shared client is accessed from Windows, replace the macOS mount path with the corresponding quoted UNC or mapped-drive path, for example:

```text
\\\\BSJT168\\BSJT 共享给我\\AI专用\\[Codex]Mac部署\\旺店通\\huice-goods-analysis
```

Keep the shared path quoted when it contains spaces or brackets. Do not rewrite the Huice workflow into ad-hoc `curl`, `.cmd`, or one-off PowerShell request wrappers.

## Safe Mutation Sequence

Before any Huice write, lock these values in evidence:

```text
supplierGoodsId, itemId, distributorGoodsId, publishId,
merchantCode, platformGoodsId, platformSkuId,
old/new price, old/new stock, controlMinPrice,
all cost inputs, both margin results, goods_detail address status
```

Perform one exact product at a time:

1. Re-read the current state immediately before writing.
2. Save only the intended price, stock, mapping, or repaired field.
3. Read publication detail back.
4. Submit one publication task only when still needed.
5. Read the current publish log and exact failure reason.
6. Read the exact official WeChat product and SKU.
7. Recompute with the actual official price.

Never let an old Huice price overwrite a newer official price during a stock-only update.

## Publish Failure Recovery

Huice save success is not platform success. If the task fails while an unsafe old price remains officially selling:

1. Delist the exact official product immediately.
2. Record the exact platform failure.
3. Repair the failure field in the existing publication; do not duplicate the product.
4. Re-read cost, floor, address, SKU mapping, category, material and stock.
5. Submit once and run an exact official readback.

Use these result labels:

```text
HARD_SUCCESS_SELLING
HARD_SUCCESS_DELISTED
ERP_STOCK_ZERO_PLATFORM_DELISTED
PRICE_UPDATE_FAILED_RISK_ISOLATED
REVIEWING_NOT_HARD_SUCCESS
MAPPING_INCOMPLETE_NO_WRITE
MISSING_COST_COMPONENT_NO_WRITE
```

Do not report `PRICE_UPDATE_FAILED_RISK_ISOLATED` as a successful price update.

## Cloud Records

Update the relevant exact rows in:

- `供销商分销状态变动记录`
- `在售限价毛利审计`
- `停供库存处理记录`
- `微信小店预计使用商品`
- `硬成功商品清单`
- `铺货复盘汇总` and `铺货复盘明细` when publication changed

At minimum record the mapping chain, old/new state, old/new price and stock, floor, cost components, both margins, `goods_detail` address status, exact request result, exact failure reason, official readback, final classification, action time and sanitized evidence path.

Read every written range back. Preserve product IDs, SKU IDs and merchant codes as text.

## Completion Report

Report separately:

1. event counts and current affected-product counts
2. official selling SKU count before and after
3. compliant, delisted, stock-zero, pending repair and missing-evidence counts
4. every mutation with its exact final classification
5. cloud sheet ranges read back
6. unresolved external blockers

Finish with a sensitive-data scan of newly created local artifacts and cloud payloads. Report only whether secret values or plaintext phone numbers were found; never print a detected secret.
