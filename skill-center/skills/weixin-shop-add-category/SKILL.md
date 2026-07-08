---
name: weixin-shop-add-category
description: Use this skill for WeChat Store / 视频号小店 merchant backend category operations, especially adding or applying for new product categories, applying leisure snack subcategories, using 《预包装食品销售备案凭证》 or other qualification materials, handling category batch-application prompts, and submitting category review in https://store.weixin.qq.com/shop/brandAndCat/category/home or related /category/apply pages.
---

# 微信小店添加类目

## Core Rule

Use Chrome DevTools MCP as the browser control surface for logged-in WeChat Store work. If `mcp__chrome_devtools` tools are not visible, discover/load the Chrome DevTools MCP tool before using any other browser automation path.

This workflow operates a live merchant backend. Stop for QR login, CAPTCHA, OTP, password, or account-security checks and ask the user to complete them. Before final submission, deletion, upload, credential change, or any other business-data mutation, confirm at action time unless the user's latest message explicitly authorizes that exact action.

## Workflow

1. Open `https://store.weixin.qq.com/shop/brandAndCat/category/home`.
2. Verify the merchant context and login state. For user-specific requests, confirm the visible store matches the requested shop before mutating anything.
3. Click `申请新类目`. The backend may open a new tab at `/shop/brandAndCat/category/apply?isShowCategorySearchModel=true`; select the newest relevant tab and close duplicates when done.
4. Choose the target category in the application modal.
   - Search by category keyword, such as `休闲零食`, then select the exact leaf path.
   - The modal is effectively single-select. For batch requests, select one eligible leaf category and use the later batch-application prompt.
   - For the leisure snack flow, known eligible leaves include `其它零食`, `膨化食品`, `豆干/素食零食`, `海味零食`, and `蛋类零食` under `食品饮料 > 休闲食品 > 休闲零食`.
5. Confirm the category and review the application page.
6. Select the required qualification. For prepackaged food, choose `《预包装食品销售备案凭证》`; prefer the page's existing reusable credential when available, and verify visible credential details instead of inventing values.
7. Submit for review only after the user has authorized the exact submission. If normal clicks fail inside the WeChat `micro-app` shadow DOM, use the DOM helpers in `references/category-application-flow.md`.
8. Handle the batch prompt:
   - If the user requested batch application for the listed categories, click `确认申请`.
   - If the user requested only the current category, click `仅申请当前类目`.
   - If the prompt lists unexpected categories or the user's intent is ambiguous, stop and ask.
9. Verify completion on the category home page. Check `生效中` and `审核中`, search/filter for the requested category names, and report which categories are effective, pending, or failed.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-add-category\\`. Any local evidence path or exported attachment path should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`. Keep paths quoted when they contain spaces, but do not rewrite this browser workflow into local shell automation.

## Detail Reference

Read `references/category-application-flow.md` before operating the live backend. It contains the observed page structure, resilient shadow-DOM helpers, and verification checks for this WeChat Store category workflow.
