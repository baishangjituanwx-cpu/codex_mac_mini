---
name: weixin-shop-yaboshi-publish
description: Select, join, publish, verify, and promote 牙博士 oral-care products for 微信小店 while enforcing the brand-managed return address from the Feishu sheet 【退货售后地址】. Use for 牙博士选品、加入分销、慧策铺货、售后地址绑定、微信销售中回查、10%普通推广、推广链接提取, or when a 牙博士 product must ignore or override goods_detail after-sale data.
---

# 牙博士微信小店铺货

Treat the Feishu brand-address row as the only after-sale address authority for every 牙博士 product. A complete or different `goods_detail` address must not override it.

## Validation status

Status: `PROVISIONAL_NOT_END_TO_END_VALIDATED`.

Passing local tests, creating drafts, receiving platform product/SKU IDs, or reaching
`审核中` proves only that the workflow is implemented. It does not prove that this
skill is stable.

Promote this skill to `END_TO_END_VALIDATED` only after one live acceptance round
completes at least three new 牙博士 products and every product satisfies all of the
following in the same run:

- Huice current publish record is successful.
- The official WeChat product and exact platform SKU are `销售中`.
- Actual price, positive stock, merchant code, and the cloud-managed address ID match.
- The 10% ordinary promotion plan is effective and returns an exact share link.
- Every required Feishu ledger write succeeds and its exact range is read back.

If any product is reviewing, rejected, missing a link, or missing cloud readback, keep
the skill provisional and record the exact failed stage. Do not describe the skill as
validated, reliable, complete, or production-ready.

## Tool boundaries

- Use the Huice shared HTTP toolkit for candidate detail, joining distribution, distribution readback, fast-publish create/query/save/submit, task logs, price, stock, and publish records.
- Use Chrome DevTools on Huice only to confirm `erp.huice.com`, refresh ephemeral authentication, or inspect a current request contract. Do not use Huice business buttons.
- Use `weixin-shop-goods-inspection` and Chrome DevTools for exact official WeChat product/SKU verification.
- Use `weixin-shop-league-ops` for the 10% ordinary all-promoters plan and exact share-link readback.
- Use `weixin-shop-price-floor-audit` for price, cost, freight, fee, and margin gates.
- Use `weixin-shop-ledger-sync` for cloud writes and exact readback.
- Never persist or report tokens, cookies, signatures, login credentials, buyer data, or plaintext phone numbers.

## Brand address gate

At candidate selection, before joining, before publish save, before publish submit, and after saved-draft readback:

1. Read the exact 牙博士 row from Feishu sheet `【退货售后地址】` in the current run.
2. Require brand, recipient, phone, province/city/district, detail, usage rule, and `微信小店地址ID` to be present.
3. Preserve the address ID as text. Do not match by recipient alone or title similarity.
4. Read the WeChat address pool and require that exact address ID to match every structured field.
5. Record `afterSaleSource=brand_cloud_override`. Do not use `goods_detail` to qualify or replace the address.
6. If the cloud row, official address, or ID is missing or inconsistent, record `BRAND_ADDRESS_MISMATCH_NO_WRITE` and do not join, save, submit, restore, or promote.

The brand address is product-specific publication data, not permission to change the shop-wide default return or shipping address.

## Candidate selection

Prefer low-after-sale-risk oral consumables and manual toothbrushes. Avoid electric toothbrushes, medical/therapeutic claims, and products with incomplete WeChat category data unless separately repaired.

For each candidate:

1. Read live supplier detail and every SKU.
2. Require supplier sale state, WeChat completeness, stock, exact `itemId/specId`, distribution cost, seller-paid freight, and `controlMinPrice`.
3. Choose the target price as the rounded-up maximum of `controlMinPrice`, both margin-floor prices, and the business band floor.
4. Require 10% promotion profit amount `> 0`, promotion margin `> 2%`, and no-promotion safety margin `>= 8%` using current platform fee, payment fee, after-sale reserve, other cost, and freight.
5. Reject missing costs as `MISSING_COST_COMPONENT_NO_WRITE`; never assume zero.
6. Check exact existing distribution and publication mappings to prevent duplicate products.

The shared candidate script accepts only a verified non-sensitive override:

```bash
node scripts/dual-platform-promotion-candidates.js \
  --platform-mode wechat \
  --category-keys oral_care \
  --brand-address-overrides '牙博士:<verified-wechat-address-id>' \
  --out outputs/current-yaboshi-candidates.json
```

Do not put the recipient, phone, or full address in command-line flags or evidence files.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher for its
business workflow. The Windows-usable equivalent is the same shared Huice HTTP flow,
read-only WeChat verification flow, and repository-root Node helper commands, so do
not fork the publication logic into ad-hoc browser or PowerShell business wrappers.

When a browser verification step needs keyboard input through `press_key`, prefer
Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is
typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-yaboshi-publish\\`. Any local
evidence path, exported candidate file, or copied share-link record should use quoted
`C:/Users/<name>/...` absolute paths instead of `/Users/...`.

Run the repository-root candidate helper from PowerShell with quoted paths rather than
adding a second launcher:

```powershell
node .\scripts\dual-platform-promotion-candidates.js `
  --platform-mode wechat `
  --category-keys oral_care `
  --brand-address-overrides "牙博士:<verified-wechat-address-id>" `
  --out "C:/Users/<name>/Downloads/current-yaboshi-candidates.json"
```

If the shared Huice toolkit is accessed from Windows, keep the mapped-drive or UNC
path quoted when it contains spaces or brackets.

## Join and publish

Process one exact SKU at a time:

1. Re-read `controlMinPrice`, current cost, freight, supply state, and brand address row.
2. Run join-distribution dry-run with the exact `supplierGoodsId + itemId`, then execute only after the user has requested publication.
3. Read the exact `distributorGoodsId` and require the selected `itemId/specId`, cost, weight, and sale state to match.
4. Create the WeChat fast-publish draft for the exact distribution product.
5. Restrict both `goodsPublishProduct` and `goodsSpecs` to the planned SKU. Any extra or missing SKU blocks submission.
6. Set `goodsPublishShipinhaoBO.afterSaleAddressId` to the fresh cloud-verified WeChat address ID.
7. Save and re-read the draft. Require exact address ID, SKU, price, stock, delivery template, cost, and mapping equality.
8. Re-read the cloud address and `controlMinPrice` again immediately before submit.
9. Submit once. Task acceptance, draft, review, and stale success rows are not hard success.

## Official success and promotion

Count a product only when all conditions hold:

- Current Huice publish record is successful with exact `publishId`, merchant code, platform product ID, and SKU mapping.
- One same-session official selling-only scan covers every page and proves displayed total = page-row sum = unique `platformGoodsId` count.
- The exact product/SKU is `销售中` with the intended actual price and positive actual stock.
- The saved publication still references the current cloud-managed brand address ID.
- Required cloud rows were written and read back exactly.

Before promotion, re-read cost, `controlMinPrice`, actual price/stock, fees, and address ID. Create only the requested 10% ordinary all-promoters plan, keep automatic/institution options off unless requested, reject duplicate plans, and accept only the share link returned for the exact product ID. Write and read back the promotion status, commission, and link.

## Completion labels

- `YABOSHI_HARD_SUCCESS_PROMOTED`: publication, official sale, address, ledger, 10% plan, and exact link all pass.
- `YABOSHI_HARD_SUCCESS_PROMOTION_PENDING`: publication passes but promotion is not yet exact and effective.
- `BRAND_ADDRESS_MISMATCH_NO_WRITE`: cloud/official/draft address evidence disagrees.
- `MAPPING_INCOMPLETE_NO_WRITE`: exact product/SKU chain is incomplete.
- `REVIEWING_NOT_HARD_SUCCESS`: submitted or under review only.
- `MISSING_COST_COMPONENT_NO_WRITE`: any required cost or fee is unknown.

Report hard-success products separately from joined, saved, submitted, reviewing, and failed products.
