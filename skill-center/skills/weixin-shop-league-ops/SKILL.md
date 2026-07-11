---
name: weixin-shop-league-ops
description: Operate and analyze the WeChat Store / 视频号小店 优选联盟 merchant backend with Chrome DevTools MCP. Use for 优选联盟、带货者推广、机构推广、活动推广、合作管理、专属营销、达人广场、机构广场、联盟规则、联盟数据, including checking alliance status, selecting products, planning commissions, inviting promoters or institutions, reviewing cooperation, and preparing or submitting promotion and activity workflows.
---

# 微信小店优选联盟运营

## Core Rules

Use Chrome DevTools MCP as the only browser-control surface unless the user explicitly requests a fallback. Read `references/shopleague-flow.md` before operating the live backend.

Treat the merchant backend as a live business system. Allow read-only navigation, filtering, screenshots, DOM inspection, console inspection, network-response inspection, and table extraction without extra confirmation when they are in scope.

Stop immediately for QR login, CAPTCHA, OTP, passwords, or account-security checks and ask the user to complete them.

Require an action-time confirmation before every state-changing operation, even when the user previously gave broad permission. This includes:

- Creating or publishing a public, targeted, or exclusive promotion plan
- Adding products to a plan or changing commission, price, scope, or expiry
- Submitting an activity application
- Inviting a promoter, creator, institution, or head supplier
- Renewing, ending, or otherwise changing a cooperation relationship
- Adding to or removing from a blacklist
- Closing 优选联盟
- Changing alliance contact information

Before requesting confirmation, state the exact action, affected products or partners, commission or price, effective period, and expected business effect. Stop on the final button and wait for an explicit confirmation that matches those details.

Never save or report cookies, tokens, magic values, authorization headers, request signatures, QR payloads, or other credentials. Do not use direct API calls to bypass the normal UI for mutations.

## Windows Compatibility

- The same Chrome DevTools MCP workflow applies on Windows; no PowerShell or `.cmd` launcher is required.
- Use Windows browser shortcuts when manual recovery is necessary: `Control+R` or `F5` to reload, `Control+L` for the address bar, `Control+A` to select all, and `Alt+Left` / `Alt+Right` to navigate history.
- Quote local evidence or export paths and use absolute Windows paths such as `C:/Users/<name>/Downloads/alliance-audit.csv`.
- The repository mirror is installed at `%USERPROFILE%\\.codex\\skills\\weixin-shop-league-ops\\`.

## Workflow

1. Open `https://store.weixin.qq.com/shop/shopleague/home` and verify the login and merchant context. Before any mutation, verify the visible shop is the requested shop; for the current workflow, expect `百亿好购店` unless the user names another shop.
2. Inspect the alliance state, rule state, clearance warnings, active plans, product eligibility, existing cooperation, activity availability, and alliance data before recommending an action.
3. Identify the requested module and follow the matching procedure in `references/shopleague-flow.md`.
4. Separate analysis from execution:
   - For analysis, produce a prioritized recommendation with evidence and leave the backend unchanged.
   - For execution, prepare the form, summarize the exact pending mutation, and request confirmation at the final action.
5. After an authorized mutation, verify the resulting UI state and report success, pending review, partial success, or failure with the affected objects.

## Operating Defaults

Use small-batch tests and cautious partner selection by default. Prefer low-refund, low-ticket, stable-stock products with enough contribution margin to cover commission and after-sales risk. For `百亿好购店`, prioritize proven oral-care items such as toothbrushes, then qualified dental-floss and selected snack products after checking their current data. Do not scale the refunded sun-protection mask, unproven high-ticket items, or products with unstable inventory.

Keep recommendations within product, pricing, commission, partner, activity, inventory, order, and after-sales operations. Do not introduce short-video or livestream production tasks unless the user explicitly expands the scope.

Do not treat old observations as current facts. Re-read the UI and current response data each run, especially activity deadlines, eligibility, product state, commission, cooperation expiry, and rule status.

## Required Reference

Read `references/shopleague-flow.md` in full before using the skill. It contains the route map, read-only audit checklist, module-specific SOPs, confirmation template, blank-page recovery procedure, current shop heuristics, and reporting format.
