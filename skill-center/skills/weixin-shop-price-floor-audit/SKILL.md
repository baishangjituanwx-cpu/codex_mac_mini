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
- Use `weixin-shop-publish-recovery` for review-blocked listings, exact SKU remapping, duplicate-listing isolation, and stock restoration after a successful republish.
- Use `weixin-shop-ledger-sync` for the cross-sheet audit trail, process-review rows, and exact cloud readback. Do not make this skill the owner of cloud write mechanics.
- Never save or output cookies, tokens, request signatures, passwords, buyer privacy, or plaintext phone numbers.

The shared HTTP reference is:

```text
/Volumes/BSJT 共享给我/AI专用/[Codex]Mac部署/旺店通/huice-goods-analysis
```

Read `docs/weixin-price-floor-and-supplier-change-audit-20260802.md` when an endpoint or historical example is needed.

## Non-Negotiable Gates

1. Treat supplier SKU `controlMinPrice` as P0. Never substitute `suggestedPrice`.
2. Resolve after-sale addresses by the shared priority rule: complete live `goods_detail` for ordinary goods; the Feishu `退货售后地址` override for 牙博士; otherwise the exact supplier's complete `saleReturnPlaces` from Huice “供销商售后退货地址”. Supplier fallback requires unique supplier identity and must be recorded as `慧策供销商售后退货地址`; incomplete or ambiguous data still blocks.
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
10. A synthesized, manually corrected, or old-snapshot-plus-delta file is never admissible as current official evidence. Capture every current official selling page in the same run, assert displayed total = returned rows = unique product IDs, and preserve page counts.

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
5. Treat a full-list `isSale=false`, `deletedStatus=1`, missing SKU, or missing distribution cost only as a stopped-supply candidate. Before any stock or sale-status mutation, re-read the exact `distributorGoodsId` through the Huice distribution-goods detail/list API and match the exact `itemId` again. Only a successful exact readback that still shows the product or SKU stopped, deleted, unavailable, or without a current cost confirms stopped supply. If the exact readback fails, record `SOURCE_STATE_RECHECK_FAILED_NO_WRITE`.

Never say that 58 event rows mean 58 currently stopped products. Re-read current state.

### 2. Build exact current facts

Capture the complete official selling list first. Paginate the current product manager in the same run and assert:

```text
official displayed total
= sum of captured page rows
= returned rows
= unique platformGoodsId count
```

Current price, stock, and selling state must come from this live capture. Historical metadata can fill immutable fields only by exact product ID.

For every affected SKU, read:

- current supplier sale/supply state
- live `distributionPrice`
- seller-paid freight and any fixed costs
- `controlMinPrice`
- current stock
- complete after-sale address and its source (`商品详情地址`, `牙博士专用地址`, or `慧策供销商售后退货地址`)
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

Price repair is the default first action. When supply is active, the live
`goods_detail` address is complete, and the mapping chain is complete, a price
floor or margin failure must be repaired by raising the existing listing price
to `targetPrice`. Keep the product selling while the safe price update is being
published. Do not zero stock or delist merely because the current price is too
low.

Only isolate the product when the price publication fails and the unsafe old
price remains exposed, or when the issue is not a price issue at all (stopped
supply, incomplete live after-sale address, or an unrepairable mapping). After
a temporary price-risk isolation, repair the existing listing and restore the
intended stock after exact official price readback passes every gate.

| Classification | Required behavior |
| --- | --- |
| `COMPLIANT` | Record and leave unchanged |
| `SUPPLIER_STOPPED_LIVE` | Only after exact `distributorGoodsId` + `itemId` readback reconfirms stopped supply, set Huice publication SKU stock to 0 and exact-read both systems; delist only if stock zero does not prevent sale or an active listing strategy can restore availability |
| `BELOW_CONTROL_MIN_PRICE` | Raise the existing listing to `targetPrice` first and keep it selling after exact official readback; isolate only if the unsafe old price remains exposed after a failed update |
| `MARGIN_FAIL` | Raise to the calculated target; if the allowed price band cannot pass, set stock to 0 and delist |
| `ADDRESS_INCOMPLETE` | Delist or keep unpublished; do not republish until a prioritized address source is complete and the source is recorded |
| `MAPPING_INCOMPLETE` | Record only; repair the mapping without creating a duplicate product |
| `REPAIRABLE_PUBLISH_FAILURE` | Repair the exact platform failure field, re-read every gate, then resubmit once |
| `SUPPLY_RECOVERED` | Record and review; never auto-list or auto-lower price |
| `COST_DECREASED` | Record and review; never auto-lower price |

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher for its browser-controlled work. The Windows-usable equivalent is the same Codex workflow: keep Chrome DevTools MCP for WeChat readback and use the shared Huice HTTP client/scripts rather than forking wrapper scripts in this repo. For supplier-address fallback, use the shared `huice-supplier-return-address` contract and record the source as `慧策供销商售后退货地址`.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-price-floor-audit\\`. Any local evidence path, exported audit path, or copied attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`.

When the Huice shared client or supplier-address contract is accessed from Windows, replace the macOS mount path with the corresponding quoted UNC or mapped-drive path, for example:

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

## Handoffs

- Hand a blocked or malformed publication to `weixin-shop-publish-recovery` only after the current price-floor and margin facts are captured.
- Hand cloud writes and process-review updates to `weixin-shop-ledger-sync`; the product decision remains owned by this audit skill.
- Hand supplier-address resolution to `huice-supplier-return-address` when the prioritized address sources require the exact supplier fallback.
- Hand distribution-order state to `huice-distribution-order-push`, and hand platform-activity submission to `weixin-shop-platform-activity-ops`. Ordinary promotion and alliance promotion are separate workflows.

### Legacy or orphan publication price repair

An old WeChat listing can remain live after the distributor product has been
recreated, leaving the current `distributorGoodsId` disconnected from the
historical `publishId`. Do not create another product and do not use the broken
chain as a reason to leave an unsafe price exposed.

When the official `platformGoodsId`, `platformSkuId`, merchant code and one
historical Huice publication still identify the same SKU exactly:

1. Read the historical publication detail and recover its `fastPublishId`.
2. Recover the exact fast-publish SKU row ID from a previously verified
   publication record; never infer it from row order or title similarity.
3. Re-read the current distributor product only for live cost,
   `controlMinPrice`, supply state and `goods_detail`.
4. Use the Huice fast-publish price batch-edit API on the historical publication
   SKU, then read the publication detail back.
5. Submit that original publication once and inspect the current task result.
6. Read the exact official WeChat product and SKU, then recompute margin using
   the actual official price.

Price repair and mapping repair are separate conclusions. The official price
can be compliant while the current distributor-to-publication chain is still
`MAPPING_INCOMPLETE_NO_WRITE`. If a live audit observes official stock 0 while
the source is still sellable but the live `goods_detail` address or current
mapping is incomplete, record the observed zero and perform no stock write; do
not actively set stock to 0 or treat the zero as a source-stop action. Do not
count the item as an effective sale or hard success until those non-price gates
are repaired.

When the publication chain is incomplete but `merchantCode/spuCode` uniquely
matches one current distributor product, use that exact match only to expose
the live source cost, `controlMinPrice`, supply state and `goods_detail` address.
Keep the final classification as `MAPPING_INCOMPLETE_NO_WRITE` until `publishId`
and platform SKU mapping are repaired; do not hide a price-floor or address risk
merely because the publication record is missing.

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

## Existing Listing SKU-Recovery Gate

When a price repair touches an existing WeChat listing, preserve the original
`goodsId + publishId + platformGoodsId`. A successful `save` or a newly created
fast-publish draft is not a substitute for repairing that original listing.

Before submitting the original listing, the same SKU row must read back with
all of these exact values:

```text
platformPrdId == current official platformSkuId
prdSn/barCode == current merchantCode
supplierItemId/itemId == current source itemId
sourceSkuId == current source skuId
distributorPrice/basePrice == current distribution cost
prdPrice/specialPrice == target price
prdNumber == intended stock
```

If the exact mapping is not preserved after `supplier/goods/publish/save`, do
not submit again. Record `MAPPING_INCOMPLETE_NO_WRITE` and wait for the active
task to finish or fail with a readable reason. Do not create successive fast
publish drafts for the same platform item. If a fast draft is used only as a
repair probe, it must carry the exact official `platformSkuId`; an old internal
`platformPrdId` is not acceptable evidence.

For the official selling-only audit, use the live `scanProductPreview` request
with both `productStatus:[5]` and `status:[5]`. The unfiltered request returns
the whole catalog, even when the page is on the selling tab. Re-read the live
API `totalNum` after any new listing, then fetch every page in the same session;
do not trust a stale tab label count. A newly created product can therefore
make two same-merchant-code rows appear: compare `platformGoodsId` and
`platformSkuId` exactly, and keep both rows separate until the Huice publish
record and source mapping identify the intended listing.

For stock semantics, distinguish three layers in every record:

```text
officialWeChatStock     = current sellable stock in the official store
huicePublishSkuStock    = stock on the Huice publication SKU
distributorSourceStock  = source/distributor available stock
```

`officialWeChatStock=0` is not evidence that the source is stopped. A product
with valid source supply, complete address and exact mapping must be repaired
by raising price or restoring the original listing stock; set stock to zero
only for a confirmed source stop, missing mandatory source data, or a failed
price repair that leaves an unsafe old price publicly exposed.

When an official selling row has `officialWeChatStock=0`, run the republish
gate before any write. Read `productId`, `skuIdList.skuIds`, `spuCode`,
`totalStockNum`, `price`, and `editStatusText` from the same live
`scanProductPreview` response. Republish is allowed only when the exact source
SKU is still sellable, current cost/freight/controlMinPrice are known,
`goods_detail` returns a complete after-sale address, and the full
`supplierGoodsId -> itemId -> distributorGoodsId -> publishId ->
platformGoodsId -> platformSkuId` mapping is exact. If another listing with the
same merchant code already has official stock above zero, do not create a
duplicate republish; repair the original listing mapping instead. A source
stop, deleted/disallowed source, missing mandatory source data, or incomplete
mapping/address is a no-republish classification and must be recorded without
changing stock. Never infer a zero-stock row from a missing or unparsed response.

If a later same-session scan shows the previously observed zero-stock row has
already returned to positive stock, treat that as a readback state change, not
as permission to submit a duplicate task. Re-read the original and any newer
same-merchant-code publication by exact `platformGoodsId`/`platformSkuId`,
then classify each row independently. If the original is still reviewing or
the newer publication still has a source-SKU or after-sale-address mismatch,
keep both rows selling at the observed compliant price, do not change stock,
and do not count either row as hard success until the mapping and
`goods_detail` gates are complete. A matching official stock value alone does
not prove that a new Huice publish task is required.

### Explicit user-directed sell-out of one duplicate listing

When the user explicitly names one exact duplicate `platformGoodsId` and asks
to make only that listing sold out, the operation is an isolation mutation, not
a supplier-stop conclusion and not a hard-success publication:

1. Read the exact official row and the matching Huice `publishId`/SKU first.
2. Preserve price, merchant code, and the sibling duplicate listing.
3. Set only the named listing's single-SKU publication stock to `0`, read it
   back, and submit the existing publication update once.
4. Read the task failure/audit result and the exact official row again. A
   successful `save` or a Huice stock value of `0` is not enough; the official
   stock must read `0` before reporting sold out.
5. If the task says the SKU does not belong to the current product, repair the
   exact `platformPrdId` mapping to the official SKU and retry once. If the
   mapping fields still do not persist or the task remains auditing, stop
   retries and report `STOCK_ZERO_UPDATE_NOT_CONFIRMED`; never change the
   sibling duplicate or claim the product is sold out.

The explicit sell-out path must remain separate from supplier-stop stock
records. It may be recorded in the price/margin, supplier-change, and publish
review ledgers, but it must never be added to the hard-success list.

### Review-blocked exact listing isolation

If an exact listing is still `审核中` and a stock or delist request returns
`10020047 商品正在审核中，请先调用撤回商品审核接口`, stop retrying that
mutation. Call the Huice HTTP API
`POST /api/admin/shipinhao/shop/goods/publish/rollback` with the exact
`{authId, platformGoodsId, goodsId, id}` tuple (`id` is `publishId`), require
`error=0`, and re-read `supplier/goods/publish/detail`. Only after the exact
identity remains unchanged may `POST /api/admin/goods/publish/isOnSale` be
retried for that one `goodsPublishId`. Then run the same-session official
`scanProductPreview` full selling-only scan.

Do not equate rollback success or Huice `goodsNumber=0` with an official
inventory field of zero. If Huice reads `publishStatus=4`, `isOnSale=0`, and
`goodsNumber=0`, and the exact `platformGoodsId` is absent from the official
selling-only full scan, classify the duplicate-sale risk as contained. Do not
touch the sibling same-merchant-code listing, do not submit a third task, and
do not count the isolation event as a hard-success publication.

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
