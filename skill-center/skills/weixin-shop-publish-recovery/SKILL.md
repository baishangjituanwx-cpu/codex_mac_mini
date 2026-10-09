---
name: weixin-shop-publish-recovery
description: Recover an exact WeChat Store listing through Huice HTTP when a publication has a broken SKU mapping, review-blocked mutation, duplicate listing, failed stock update, or zero official stock that should be restored.
---

# 微信小店原刊登恢复与重复刊登隔离

Recover the existing exact listing. This skill is not a product-creation skill and must never create a new product merely because an old listing has a bad SKU row.

## Rules

- Huice business operations use the shared HTTP API; official WeChat verification is read-only and same-session.
- Keep Huice publication stock, distributor available stock, and official WeChat inventory as three separate values.
- Lock the exact `supplierGoodsId -> itemId -> distributorGoodsId -> publishId -> merchantCode/outerId -> platformGoodsId -> platformSkuId` chain before any write.
- A review-block error requires exact rollback, detail readback, and only then an exact-listing mutation. Never retry blindly.
- Repair `platformPrdId` from the exact official SKU; never infer it from title, row order, or image similarity.
- Submit at most one current task and do not count accepted, queued, reviewing, or audit states as success.
- Run the dynamic official full scan and validate displayed total = page-row sum = returned rows = unique exact IDs.
- Hand price/cost/margin decisions to `weixin-shop-price-floor-audit` and cloud rows to `weixin-shop-ledger-sync`.
- Never expose credentials or buyer privacy.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is still the same Huice shared HTTP workflow plus the read-only official WeChat verification flow, so do not fork this repo into ad-hoc browser, `curl`, or PowerShell business wrappers.

When a browser verification step needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-publish-recovery\\`. Any local evidence path, saved response file, or copied attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`.

For the validator command in PowerShell, keep the live response path quoted, for example:

```powershell
node scripts/validate-weixin-selling-scan.js "C:/Users/<name>/Desktop/live-raw.json" --target <platformGoodsId>
```

## Completion Classes

`RECOVERED_HARD_SUCCESS`, `REVIEWING_NOT_HARD_SUCCESS`, `ISOLATED_DUPLICATE_CONTAINED`, `MAPPING_INCOMPLETE_NO_WRITE`, and `SOURCE_STATE_RECHECK_FAILED_NO_WRITE` are separate outcomes. A zero-stock duplicate isolation is not a hard success.
