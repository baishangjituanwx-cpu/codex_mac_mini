---
name: huice-distribution-order-push
description: Diagnose, resolve, verify, and safely push Huice/Wangdiantong outsourced distribution orders through the ERP HTTP API with exact-order matching, state-driven decisions, automatic-push awareness, balance-failure recovery, idempotency, polling, success verification, attribution, and sanitized evidence. Use when Codex needs to check 待发货-委外, investigate 待推单/推单失败/推单中/推单成功, find and resolve a concrete failure reason, watch automatic retry after recharge, verify a successful supplier order, execute a guarded manual 推单, or determine whether Huice automatic push or Codex caused success.
---

# Huice Distribution Order Push

Use HTTP API calls for order reads and mutations. Use `chrome-devtools-mcp` only to access the already authenticated Huice page context or discover the current request contract; do not click ERP business buttons.

## Invariants

- Treat the exact platform order number as the primary lookup key.
- Read all four push states before deciding what to do: 待推单, 推单失败, 推单中, 推单成功.
- Default to read-only. Perform a write only when the current request authorizes pushing.
- Submit at most one mutation for an exact `tradeId` in one run.
- Skip mutation when the preflight state is 推单中 or 推单成功.
- Never count a validation response, dashboard count, or request acceptance as business success.
- Never stop at a status label: diagnose failures and verify successful supplier-order evidence.
- Continue the state loop after a remediation until success is verified or a concrete external blocker remains.
- Attribute success from timestamps and API evidence. Never claim an earlier automatic push as a Codex action.
- Append every completed push investigation to the cloud sheet `分销订单推单记录` and read the exact row back. A missing ledger row means the workflow is not complete.
- Never save or print cookies, tokens, buyer details, phone numbers, or full addresses.

## State Decision Loop

| Current state | Required behavior | Completion condition |
| --- | --- | --- |
| 待推单 | Verify exact order and automatic-push queue; observe first, then submit once only when authorized and still needed | Transitions to 推单中/推单成功, or a concrete failure is diagnosed |
| 推单失败 | Read exact `errorMsg`, classify the cause, identify the owner and corrective action; do not blindly retry | Corrective action is completed and the order is re-queried |
| 推单中 | Poll the exact order; never submit again | Becomes 推单成功 or 推单失败 with an exact reason |
| 推单成功 | Verify push time, outsource order number, supplier, product/SKU, quantity, cost, and refund state | Exact order is successful and verification evidence is complete |

Treat the workflow as a loop, not a one-time API call:

```text
query -> diagnose -> resolve/observe -> re-query -> verify -> report
```

## Workflow

1. Confirm authentication and execution boundary.
   - Prefer a logged-in Huice tab and same-origin HTTP requests through `chrome-devtools-mcp`.
   - If `HUICE_MAIN_COOKIE` is already available ephemerally, use the bundled CLI. Never extract or echo it into chat or evidence.
   - This account has Huice automatic push enabled. Treat balance recovery as capable of triggering an automatic retry.

2. Locate the exact order.
   - Query `/api/main/oms/tradeQuery/query` with `pageTab=WAIT_SEND_CLOUD` across push states `1..4`.
   - Match only the exact platform order number; do not select by product title alone.
   - Capture sanitized identifiers and facts: `tradeId`, platform order, shop, platform, supplier, product/SKU IDs, quantity, paid amount, distribution cost, refund state, push state, push time, failure reason, and outsource order number.

3. Run preflight guards.
   - Verify expected shop and platform.
   - Stop on refund/after-sales conflict, missing `tradeId`, ambiguous duplicate match, or order mismatch.
   - If state is 推单中 or 推单成功, do not submit again.

4. Diagnose the current state.
   - For 推单成功, verify strong evidence instead of merely echoing the label.
   - For 推单失败, preserve the exact reason and map it to a corrective action. Read the failure decision table in `references/api-and-attribution.md`.
   - For 推单中, poll without mutation.
   - For 待推单, prefer observing the enabled automatic-push mechanism before a guarded manual request.

5. Handle balance failures correctly.
   - Record the actual available balance and required amount when the failure message provides them.
   - Do not recharge, pay, or alter supplier funds.
   - After the user recharges, query the order again before any manual push because Huice may retry automatically.
   - Use read-only watch mode after recharge. Continue until the state changes or the watch window expires.
   - If the order becomes successful without a valid Codex mutation, attribute it to Huice automatic push and then run full success verification.

6. Submit only when still necessary.
   - POST `/api/main/oms/omsPushOrder/pushOrder`.
   - Send the body exactly as `{"source":0,"tradeIdList":["<exact tradeId>"]}`.
   - Do not wrap this body in `data`, `params`, `payload`, or another object.
   - A `tradeIdList must not be null/empty` response is a request-contract failure, not a business push and not permission to submit repeatedly.
   - A failed order requires diagnosed remediation before a manual retry. Pass `--failure-remediated` only after that remediation is known to be complete.

7. Poll and classify.
   - Re-query the four states after submission until 推单成功, 推单失败, or the polling window expires.
   - Treat 推单成功 plus matching push time, outsource order number, supplier and SKU facts as verified completion evidence.
   - Report the exact failure text when unsuccessful; do not replace it with a guessed cause.

8. Record evidence and report attribution.
   - Write only sanitized evidence under `outputs/` with preflight, mutation response, polling, final state, and attribution.
   - State separately: current business result, whether Codex issued a mutation, and who/what most likely caused success.
   - Record `diagnosis`, `recommendedAction`, `actionOwner`, `verification`, and `nextAction`.

9. Update and verify the operating ledger.
   - Use the active business workbook and the sheet `分销订单推单记录`; create it only when it does not exist.
   - Write the exact platform order, Huice `tradeId`, Huice order number, supplier, product/SKU, amount, distribution cost, preflight state, exact sanitized failure reason, remediation, final state, push time, outsource order number, success attribution, duplicate guard, and next action.
   - Preserve order and ID columns as text. Never write buyer data, credentials, full addresses, or token-bearing evidence.
   - Read the exact written row back. Do not report the order-push workflow as complete if the write or readback fails.

## Bundled CLI

Use [`scripts/huice-push-distribution-order.js`](scripts/huice-push-distribution-order.js) when an ephemeral `HUICE_MAIN_COOKIE` is already present.

When this mirror is used on Windows, prefer the bundled PowerShell launcher [`scripts/huice-push-distribution-order.ps1`](scripts/huice-push-distribution-order.ps1) instead of rewriting the CLI examples into ad hoc `cmd.exe` syntax.

Read-only inspection:

```bash
HUICE_MAIN_COOKIE="$HUICE_MAIN_COOKIE" node scripts/huice-push-distribution-order.js \
  --platform-order 1234567890123456789
```

Watch automatic retry after recharge without submitting anything:

```bash
HUICE_MAIN_COOKIE="$HUICE_MAIN_COOKIE" node scripts/huice-push-distribution-order.js \
  --platform-order 1234567890123456789 \
  --watch \
  --poll-attempts 12
```

Single guarded push:

```bash
HUICE_MAIN_COOKIE="$HUICE_MAIN_COOKIE" node scripts/huice-push-distribution-order.js \
  --platform-order 1234567890123456789 \
  --execute
```

Retry a previously failed order only after its diagnosed cause has been resolved:

```bash
HUICE_MAIN_COOKIE="$HUICE_MAIN_COOKIE" node scripts/huice-push-distribution-order.js \
  --platform-order 1234567890123456789 \
  --execute \
  --failure-remediated
```

The CLI defaults to platform `83` and shop `百亿好购店`. Override only after verifying the target:

```bash
node scripts/huice-push-distribution-order.js \
  --platform-order 1234567890123456789 \
  --platform-id 83 \
  --shop-name 百亿好购店
```

## Windows Repo Mirror Notes

This skill keeps the same Node CLI and authenticated-browser workflow on Windows; it does not fork a separate business implementation. Use the bundled PowerShell launcher when a Windows operator needs a local entry point:

```powershell
$env:HUICE_MAIN_COOKIE = '...'
.\scripts\huice-push-distribution-order.ps1 --platform-order 1234567890123456789
```

Windows read-only watch after a supplier recharge:

```powershell
$env:HUICE_MAIN_COOKIE = '...'
.\scripts\huice-push-distribution-order.ps1 `
  --platform-order 1234567890123456789 `
  --watch `
  --poll-attempts 12
```

Windows guarded execute after remediation:

```powershell
$env:HUICE_MAIN_COOKIE = '...'
.\scripts\huice-push-distribution-order.ps1 `
  --platform-order 1234567890123456789 `
  --execute `
  --failure-remediated
```

When a browser interaction needs keyboard recovery through `press_key`, use Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\huice-distribution-order-push\\`. Keep local evidence paths quoted and in `C:/Users/<name>/...` form. Do not dump `HUICE_MAIN_COOKIE` into PowerShell history, tracked files, screenshots, or cloud docs.

## Reporting Contract

Always return these fields:

- 平台订单号 and 慧策 `tradeId`
- 商品、规格、数量 and supplier
- 推单前状态 and exact failure reason
- Failure category, corrective action, action owner, and whether automatic retry is expected
- 是否发起 HTTP API 写请求
- 写请求 response, without secrets
- 最终推单状态, push time, and outsource order number
- 成功核实是否完整 and any missing verification fields
- Success attribution: Huice automatic push, Codex HTTP API, external/manual action, or unresolved
- Cloud-sheet range and exact-row readback result
- Next required action

For endpoint schemas and attribution rules, read [`references/api-and-attribution.md`](references/api-and-attribution.md).
