---
name: pinduoduo-product-management
description: Use this skill for Pinduoduo / 拼多多 merchant-backend product management in mms.pinduoduo.com, including inspecting sales-state tabs, searching and listing goods, reading product parameters and SKU data, checking product health, viewing product data or previews, and safely editing titles, categories, attributes, images, descriptions, prices, stock, freight, shipping promises, publish/unpublish state, or drafts. Trigger for requests such as 查看在售商品, 查看商品参数, 商品管理, 编辑商品, 改价, 改库存, 商品上下架, or auditing a Pinduoduo goods list.
---

# 拼多多商品管理

## Core Rules

Use the `mcp__chrome_devtools` namespace as the browser control surface. Start with `list_pages`, take a current snapshot before every interaction, and do not switch to another browser automation surface unless the user explicitly requests a fallback.

Treat `mms.pinduoduo.com` as a live business system:

- Verify the visible shop name matches the merchant requested by the user before changing anything.
- Allow read-only navigation, filtering, searching, table extraction, opening product details, screenshots, previews, and diagnostics without extra confirmation.
- Before changing a title, category, attribute, image, description, SKU, price, stock, freight template, shipping promise, service commitment, publish state, draft, or any batch setting, confirm the exact product and exact change at action time unless the user's latest message already authorizes that exact mutation.
- Never click `提交`, `保存草稿`, `上架`, `下架`, `删除`, or a batch-action confirmation without current authorization for that exact action.
- Stop for login, password, OTP, QR confirmation, CAPTCHA, slider puzzle, or account-security verification. Ask the user to complete it manually, then re-check the page state.
- Re-read live values on every run. Counts, statuses, prices, stock, and page structure are dynamic; never treat examples in this skill as current shop data.

## Workflow

1. Open the user-provided route or `https://mms.pinduoduo.com/goods/goods_list?msfrom=mms_sidenav`.
2. Verify login state, current URL, visible shop name, and requested product scope.
3. Select the requested status tab such as `在售中`, `已下架`, `已售罄`, `发布中`, `已驳回`, or `草稿箱` from a fresh snapshot.
4. Search by product ID, product code, SKU code, or product name when the user gives a target. Use the visible query controls and `查询`; use `重置` before changing search strategy.
5. Extract rows from the snapshot or a bounded, read-only DOM inspection. Capture product name, product ID, product code, price, total stock, favorites, cumulative sales, 30-day sales, product-health state, created time, sales state, and available actions.
6. If the requested count exceeds visible rows, inspect pagination and continue until the requested scope is complete. Reconcile extracted rows with the visible `共有 N 条` count.
7. To inspect parameters, open the row's `编辑` link without changing fields. Read `references/product-management-flow.md` before inspecting or changing a product.
8. When the default snapshot exposes `编辑` only as `StaticText`, take a verbose snapshot and click its ancestor `link "编辑"` UID. Product details commonly open in a new tab; call `list_pages`, select the new page, and close duplicate temporary tabs when finished.
9. For read-only requests, report the observed live values and explicitly state that no data-changing action was performed.
10. For authorized mutations, change only the requested fields, review the resulting values before submission, obtain any required action-time confirmation, submit once, and verify the resulting status or list value after the page settles.

## Loading Recovery

If the goods page remains on a spinner, inspect `document.readyState`, visible text, iframes, console errors, and XHR/fetch/script requests. Follow the Pinduoduo loading-recovery procedure in the `chrome-devtools-mcp` skill, including the static-host rewrite only after confirming a failed `mms-static.pddpic.com` asset.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\pinduoduo-product-management\\`. Any local evidence path, exported report path, or copied attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`. Keep paths quoted when they contain spaces, but do not rewrite this browser workflow into local shell automation.

## Detail Reference

Read [references/product-management-flow.md](references/product-management-flow.md) for the observed list controls, row schema, product-detail field map, tested example, mutation checklist, and verification rules.
