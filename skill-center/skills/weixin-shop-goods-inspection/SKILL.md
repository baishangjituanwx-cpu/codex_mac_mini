---
name: weixin-shop-goods-inspection
description: Inspect and report WeChat Store / 视频号小店 product-list status with Chrome DevTools MCP. Use for 商品列表、销售中、已下架、审核中、审核待处理、审核未通过、草稿箱、回收站, product counts, pagination, product IDs, prices, inventory, recent sales/exposure, information-adjustment warnings, listing strategy, listing time, and read-only product exports in https://store.weixin.qq.com/shop/goods/list.
---

# 微信小店商品状态检查

## Core Rules

Use Chrome DevTools MCP as the browser-control surface. Read `references/goods-list-flow.md` before inspecting the live merchant backend.

Treat navigation, filtering, screenshots, status-detail viewing, pagination, table extraction, and read-only export as non-mutating operations. Stop for QR login, CAPTCHA, OTP, passwords, or account-security checks and ask the user to complete them.

Require action-time confirmation before every operation that can change merchant data, including editing a product, using 免审编辑, changing stock or price, publishing, listing, delisting, hiding, copying, deleting, restoring, changing content, creating an evaluation campaign, or running any batch mutation. State the exact product IDs, old and new values, scope, and expected effect before the final action.

Never save or report cookies, tokens, authorization headers, request signatures, QR payloads, or other credentials. Do not call private mutation APIs directly.

## Inspection Workflow

1. Open the user-specified goods-list URL or `https://store.weixin.qq.com/shop/goods/list`.
2. Verify login state and merchant context. Before any future mutation, verify the visible shop matches the requested shop; for the current operating context, expect `百亿好购店` unless the user names another store.
3. Capture the counts for 全部、销售中、已下架、审核中、审核待处理、草稿箱 and 回收站.
4. Select the requested tab with the current snapshot identifier.
5. Wait for the table total and visible row statuses to refresh. Do not trust `currentTab` alone: the URL can retain `PRODUCT_STATUS_CHECK_FAIL` after the UI has switched to 销售中.
6. Extract visible rows from the `micro-app` shadow root when the accessibility snapshot is stale or contains rows from the previous page.
7. Traverse every page, wait for visible product IDs to change, and deduplicate by product ID.
8. Verify that the unique row count matches the displayed total. Report mismatches as incomplete extraction.
9. Report product name, ID, price, stock, pending-payment stock, recent sales, historical sales, exposure, health warning, sales state, listing strategy, listing time, and available actions when present.
10. State explicitly that no product data was changed during a read-only inspection.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-goods-inspection\\`. Any local evidence path, exported report path, or copied attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`. Keep paths quoted when they contain spaces, but do not rewrite this browser workflow into local shell automation.

## Reporting Defaults

Summarize the store-level counts first, then list the requested products. Highlight:

- Products with `信息待调整` or unresolved review failures
- Duplicate or near-duplicate titles with different product IDs
- Zero-stock or unusually low-stock products
- Products controlled by `上架策略生效中`
- Products with nonzero sales, exposure, or platform recommendations
- Count differences between tabs or pagination totals

Label the extraction date and source page. Treat all product data as a point-in-time observation and re-read the backend on every run.

## Required Reference

Read `references/goods-list-flow.md` in full before operating. It contains the route behavior, state-verification rules, pagination procedure, bounded DOM extractor, failure-reason workflow, and report format.

When the request involves supplier `controlMinPrice`, price-floor violations, cost or freight changes, margin recalculation, stopped supply, inventory zeroing, or remediation across Huice and WeChat, also use `weixin-shop-price-floor-audit`. This inspection skill proves the official product state; it does not replace the Huice-side SKU mapping and cost audit.
