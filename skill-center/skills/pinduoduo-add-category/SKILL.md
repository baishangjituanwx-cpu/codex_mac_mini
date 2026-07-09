---
name: pinduoduo-add-category
description: Use this skill for Pinduoduo / 拼多多 merchant backend category and qualification operations, especially adding or enabling a shop category such as 休闲零食, finding the correct route for food categories, uploading 仅销售预包装食品备案凭证 / 预包装食品销售备案凭证, handling Pinduoduo 店铺信息-类目资质 or 店铺经营许可证 pages, and submitting category or operating-license review in https://mms.pinduoduo.com.
---

# 拼多多添加类目

## Core Rules

Use Chrome DevTools MCP as the browser control surface. If `mcp__chrome_devtools` tools are not visible, discover/load the Chrome DevTools MCP tool before using any other browser automation path.

This workflow operates a live merchant backend. Stop for QR login, password, OTP, account-security prompts, CAPTCHA, slider puzzles, or any human verification. Pinduoduo slider verification can appear after clicking `提交`; treat visual prompts such as `请向右滑块完成拼图` as human verification even if the accessibility snapshot is incomplete.

Before final submission, deletion, upload, credential change, or any other business-data mutation, confirm at action time unless the user's latest message explicitly authorizes that exact action.

## Workflow

1. Open `https://mms.pinduoduo.com/goods/goods_list` or the direct backend route the user provides.
2. Verify login and visible shop context. For user-specific work, ensure the shop name matches the requested merchant before mutating anything.
3. Determine the correct route:
   - For food/leisure snack requests such as `休闲零食`, do not assume `店铺信息 > 类目资质` is the right place. On Pinduoduo, this often requires `店铺信息 > 店铺经营许可证 > 添加证照 > 食品经营许可 > 仅销售预包装食品备案凭证`.
   - For non-food or explicitly listed special categories, inspect `店铺信息 > 类目资质` and apply only if the exact category is available.
4. For `仅销售预包装食品备案凭证`, read `references/category-application-flow.md` before operating the live backend.
5. Fill only values that are visible in the credential or confidently provided by the user. Do not invent certificate numbers, expiration dates, business scopes, administrator names, or official lookup URLs.
6. Upload the credential image/file only after the user has provided or confirmed it. Verify upload success by checking for a `预览` link or equivalent uploaded-file state.
7. Click `提交` only after the user's latest message authorizes the exact submission. If a final confirmation appears, read it and continue only if authorized.
8. After submission, explicitly check for human verification before reporting completion. If a slider/CAPTCHA appears, stop and ask the user to complete it, then verify the final status after the user confirms.
9. Verify completion on the list/detail page. Report the visible status such as `审核中`, `审核通过`, `驳回`, submitted date, and platform estimate.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\pinduoduo-add-category\\`. Any local evidence path or exported attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`. Keep paths quoted when they contain spaces, but do not rewrite this browser workflow into local shell automation.

## Detail Reference

Read `references/category-application-flow.md` for the observed Pinduoduo page paths, field mappings for `仅销售预包装食品备案凭证`, and verification checklist.
