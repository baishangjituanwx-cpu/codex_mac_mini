---
name: wechat-shop-return-address
description: Manage and select WeChat Shop after-sales and return addresses for product-listing workflows through the logged-in merchant backend. Use when Codex needs to inspect the address pool, prevent duplicate addresses, add or edit a courier address, set or preserve the shop-wide default return address, obtain an address ID, or verify the specific after-sales address before publishing products to 微信小店.
---

# 微信小店售后地址铺货流程

## Core Rules

Use Chrome DevTools MCP as the browser-control surface for logged-in WeChat Shop work. If `mcp__chrome_devtools` tools are not visible, discover or load that MCP tool before using any other browser automation path.

This workflow operates a live merchant backend. Stop for QR login, CAPTCHA, OTP, password, or account-security checks and ask the user to complete them. Before every business-data mutation, confirm at action time unless the user's latest message already authorizes that exact action.

Treat the global `默认退货地址` as a shop-wide setting. Do not change it when selecting an address for a single listing unless the user explicitly asks to change the store default.

## Workflow

1. Open `https://store.weixin.qq.com/shop/address/expressAddressMgmt`.
2. Verify login state and merchant context before touching any address data.
3. Search the existing address pool first. Match by address ID when possible; otherwise cross-check contact name, phone number, province/city/district, detailed street address, and any visible usage labels.
4. If a complete match already exists, reuse that address and record the address ID instead of creating a duplicate.
5. If the address exists but the information is wrong, locate the target row by address ID first, then edit only the required fields.
6. If the address does not exist, open `新增地址`, prefer the backend's address-recognition helper when the full address is available, and manually verify every parsed field before saving.
7. Before any `保存`, `更新`, `删除`, default-address toggle, or product publish action, report the address ID or pending values plus any default-address impact and get action-time confirmation.
8. After saving or updating, return to the list, verify the visible row, and record the system address ID.
9. During product listing or publishing, select the verified after-sales address by address ID when the UI exposes it. If the picker hides IDs, cross-check contact, masked phone, region, and detailed address before confirming.
10. Before the final publish step, restate the product, selected address ID, contact, and address summary, then obtain the publish confirmation required by the listing flow.

## Detailed Address Rules

When adding or editing an address, verify each field explicitly:

- contact name is required and should not exceed the page limit
- phone number is required
- province, city, and district or county must match the supplier or user-provided source
- detailed address must not repeat province, city, or district text
- postal code is optional and should only be filled when provided

When the page offers address-usage toggles:

- `默认发货地址`: set only if the user explicitly requests it
- `默认退货地址`: set only if the user explicitly requests a shop-wide default change

Never identify an editable row only by contact name. Similar names and reused phone numbers can exist in the same address pool.

## Mutation Boundary

Read-only inspection includes opening the address page, searching, filtering, reading fields, opening an add or edit dialog without submitting, and gathering the current address ID.

The following actions mutate business data and require confirmation immediately before the click:

- `保存`
- `更新`
- `删除`
- changing `默认发货地址`
- changing `默认退货地址`
- selecting the final after-sales address in a publish flow when it changes what the product will use
- publishing the product

Do not delete addresses just because they look duplicated or old. Deletion requires a user-specified address ID and a second confirmation before the destructive action.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back and forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\wechat-shop-return-address\\`. Any local evidence path, exported address screenshot path, or attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`. Keep paths quoted when they contain spaces, but do not rewrite this browser workflow into local shell automation.

## Failure Handling

- If a snapshot `uid` becomes stale, refresh the snapshot before continuing.
- If the page stalls, check readiness state, iframe context, console errors, and recent network activity before retrying.
- If address recognition fills incorrect values, clear the incorrect fields and correct them manually before saving.
- If the saved address does not appear immediately, refresh and search by phone number, detailed address, or address ID before retrying or concluding failure.
- If a security check appears, stop and wait for the user.

## Reporting

Report:

- the opened page and login state
- whether the address was found, reused, added, or edited
- the address ID involved
- whether the default shipping or default return address changed
- whether any save, update, delete, or publish action was executed
- `未改变微信小店业务数据` when no mutation was performed
