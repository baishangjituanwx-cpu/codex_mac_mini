# API And Attribution Reference

## Contents

- Authentication boundary
- Order query
- Push mutation
- State interpretation
- State-driven decision loop
- Failure diagnosis table
- Automatic-push and balance workflow
- Success attribution
- Evidence schema
- Known failure patterns

## Authentication Boundary

Preferred execution is a same-origin HTTP request in an already authenticated Huice page context. `chrome-devtools-mcp` may provide that context, but do not use browser clicks to advance the business workflow.

In `chrome-devtools-mcp`, select the logged-in `https://erp.huice.com/` page and use `evaluate_script`. Build requests inside the page so the browser attaches its authenticated session without exposing it:

```javascript
async (endpoint, body) => {
  const response = await fetch(endpoint, {
    method: "POST",
    credentials: "include",
    headers: {
      accept: "application/json, text/plain, */*",
      "app-code": "web",
      "app-product-code": "jisu",
      "content-type": "application/json"
    },
    body: JSON.stringify(body)
  });
  return await response.json();
}
```

Return only a sanitized projection from `evaluate_script`; never return the browser cookie jar, storage values, request authorization headers, or an unfiltered order response.

For the bundled Node CLI, pass the current session only through `HUICE_MAIN_COOKIE`. Keep it ephemeral. Never write it to source, shell history, JSON evidence, cloud documents, or chat.

On Windows PowerShell, set the cookie only for the current shell session with `$env:HUICE_MAIN_COOKIE = '...'`, then invoke [`../scripts/huice-push-distribution-order.ps1`](../scripts/huice-push-distribution-order.ps1). Do not switch to `setx`, persist the cookie in the registry, or place it inside a `.ps1` file.

Common request headers used by the Huice main ERP API:

```text
accept: application/json, text/plain, */*
app-code: web
app-product-code: jisu
app-version: <current web version>
content-type: application/json
origin: https://erp.huice.com
```

## Order Query

Endpoint:

```text
POST https://erp.huice.com/api/main/oms/tradeQuery/query
```

Use `pageTab=WAIT_SEND_CLOUD`. The important status filters are:

| `pushStatusFast` | Meaning |
| --- | --- |
| `1` | 待推单 |
| `2` | 推单失败 |
| `3` | 推单中 |
| `4` | 推单成功 |

Search every state because an automatic retry can move an order while Codex is working. Paginate until the exact platform order number is found or the result set is exhausted.

Exact platform order candidates are typically exposed as `srcTids`, `srcTid`, or `tid`. Normalize to string and require exact equality.

Important sanitized fields:

| Meaning | Typical field |
| --- | --- |
| Huice trade ID | `tradeId` |
| Huice order number | `tradeNo` |
| Platform order | `srcTids` / `srcTid` / `tid` |
| Shop | `shopName` |
| Platform | `platformId` |
| Supplier | `providerName` / item `providerName` |
| Supplier account | `providerNickNo` |
| Platform product/SKU | item `apiSpuId` / `apiSkuId` |
| Product/specification | item `spuName` / `skuName` |
| Distribution cost | item `omsPurchaseAmount`, order `fenxiaoCostPrice` |
| Push state text | `tradeStatusFrontText` or status filter used to find row |
| Push time | `pushDate` |
| Outsource order | `outsourceNo` |
| Failure reason | `errorMsg` |

Do not preserve buyer nickname, recipient, phone, delivery address, or raw response bodies.

## Push Mutation

Endpoint:

```text
POST https://erp.huice.com/api/main/oms/omsPushOrder/pushOrder
```

Correct body:

```json
{
  "source": 0,
  "tradeIdList": ["<exact tradeId>"]
}
```

Rules:

- Use an array even for one order.
- Use the Huice `tradeId`, not platform order number, `tradeNo`, product ID, or SKU ID.
- Send this object as the top-level JSON body.
- Submit no more than once in a run.
- Re-query before submission and skip if the state is already 推单中 or 推单成功.

## State Interpretation

Do not infer success from HTTP 200 alone.

| Evidence | Interpretation |
| --- | --- |
| Query row is 推单成功 | Business success |
| Matching `outsourceNo` exists | Strong supplier-order evidence |
| Mutation response names target in success list | Mutation accepted for exact order |
| Query row is 推单中 | In progress; do not resubmit |
| Query row is 推单失败 with `errorMsg` | Failed; report exact reason |
| Validation error with empty success list | No business push |
| Dashboard count changed | Discovery hint only, never final evidence |

## State-Driven Decision Loop

Do not return a bare status. Produce a decision object for every query:

```json
{
  "state": "推单失败",
  "category": "supplier_balance_insufficient",
  "exactReason": "<sanitized exact ERP reason>",
  "actionOwner": "user",
  "recommendedAction": "Recharge the cooperating supplier balance, then run read-only watch mode.",
  "allowMutationNow": false,
  "shouldPoll": true,
  "autoRetryExpected": true,
  "completionCondition": "The exact order becomes verified 推单成功."
}
```

Use these tendencies:

| State | Decision tendency |
| --- | --- |
| 待推单 | Observe automatic push first; submit once only when authorized and still pending after a fresh check |
| 推单失败 | Diagnose exact cause and resolve it before retrying |
| 推单中 | Poll only; never resubmit |
| 推单成功 | Verify exact supplier-order evidence; do not stop at the label |

For successful verification, require the exact `tradeId` and platform order plus these facts when the API exposes them:

- `pushTime`
- `outsourceOrderNo`
- supplier name/account
- platform product ID and SKU ID
- specification and quantity
- distribution cost
- no refund conflict

Missing logistics number immediately after push does not invalidate push success. Record it as a later fulfillment follow-up.

## Failure Diagnosis Table

Always preserve the sanitized exact ERP reason in addition to the category.

| Failure signal | Category | Corrective action | Retry tendency |
| --- | --- | --- | --- |
| 余额不足、可用余额不足、金额不足 | `supplier_balance_insufficient` | User recharges the cooperating supplier balance; then watch automatic retry | Do not manually retry before recharge; re-query first afterward |
| 库存不足、无库存、缺货 | `supplier_stock_unavailable` | Recheck exact supplier SKU stock and availability; coordinate supplier or replace item | No blind retry |
| 价格变动、采购价/分销价变化、金额不一致 | `supplier_price_changed` | Refresh current SKU cost and recalculate order economics | Retry only after cost and margin are accepted |
| 商品/SKU不存在、已下架、映射失败、规格不匹配 | `supplier_sku_mapping_invalid` | Verify supplier goods state and exact SKU mapping | Retry only after mapping/supply is repaired |
| 不配送、地区限制、物流模板异常、地址不可达 | `delivery_restriction` | Verify serviceable region and supplier logistics without exposing buyer address | Retry only after a valid delivery route exists |
| 供应商未合作、授权失效、店铺停用 | `supplier_authorization_invalid` | Restore cooperation/authorization or choose another supplier | No retry until relationship is valid |
| 登录失效、鉴权失败、token过期 | `authentication_failure` | Refresh the authenticated Huice session | Re-query before any mutation |
| `tradeIdList` null/empty or request schema validation | `request_contract_error` | Correct the top-level request body | Re-query first; at most one corrected request |
| Empty/unknown `errorMsg` | `unknown_failure` | Inspect exact order details, push logs, and API response | No blind retry; escalate with evidence |

If multiple signals appear, prioritize the business blocker over a secondary technical message and retain all exact messages in evidence.

## Automatic-Push And Balance Workflow

This Huice account has automatic push enabled.

When the failure reason says the supplier balance is below the required distribution amount:

1. Record available balance and required amount when present.
2. Do not modify funds.
3. Wait for the user to recharge or confirm recharge.
4. Immediately re-query the exact order across all four states.
5. If success appears before Codex makes a valid mutation, record Huice automatic retry as the cause.
6. Only make one manual API push if the order remains 待推单/推单失败 and execution is authorized.

Validated transition example:

```text
推单失败（供应商余额不足）
-> user recharges
-> Huice automatic push retries
-> exact order becomes 推单成功
-> verify pushTime + outsourceOrderNo + supplier/SKU/cost
-> attribute success to Huice automatic push
```

The workflow is incomplete at both “recharge completed” and “status changed to success.” It completes only after the exact successful order is verified.

## Success Attribution

Capture these timestamps:

- `preflightCheckedAt`
- `mutationAttemptedAt`
- `mutationCompletedAt`
- ERP `pushTime`
- Every polling `checkedAt`

Classify conservatively:

| Condition | Attribution |
| --- | --- |
| Preflight already shows 推单成功 | `huice_auto_or_external_before_codex` |
| Automatic push is enabled and success follows recharge before mutation | `huice_auto_push_before_codex` |
| Preflight shows 推单中 and Codex skips | `huice_auto_or_external_processing` |
| Mutation explicitly returns target `tradeId` in success list and later query succeeds | `codex_http_api_confirmed` |
| Mutation returns a contract/validation failure but query is already successful | `not_codex_http_api` |
| Push time predates `mutationAttemptedAt` | `not_codex_http_api` |
| Success occurs after mutation but response does not identify target and automatic push is enabled | `unresolved_auto_or_codex` |
| Read-only watch observes failed/pending order become successful with no Codex mutation | `huice_auto_push_observed_by_codex` |

Never upgrade `likely` or `unresolved` to `confirmed` without direct evidence.

## Evidence Schema

On Windows, the evidence file should still be per-run, sanitized, and user-scoped. Keep the path quoted and in `C:/Users/<name>/...` form, and do not loosen NTFS ACLs just to mimic Unix chmod semantics.

Write a mode-`0600` JSON file containing only:

```json
{
  "schemaVersion": 2,
  "recordedAt": "ISO-8601",
  "platformOrder": "...",
  "mode": "read_only | execute_once",
  "autoPushEnabled": true,
  "preflight": {},
  "preflightDecision": {},
  "submission": {},
  "polling": [],
  "final": {},
  "attribution": {},
  "decision": {}
}
```

Scan the output for `Cookie`, `X-HC-TOKEN`, token-like values, mobile numbers, and raw addresses before reporting completion.

## Cloud Spreadsheet Ledger Contract

Every investigated outsourced distribution order must be appended to the active business workbook sheet `分销订单推单记录` and then read back by exact range. At minimum record:

- record time and business date
- platform, shop, platform order number, Huice `tradeId`, and Huice order number
- platform product ID, platform SKU ID, product, specification, quantity, paid amount, and distribution cost
- supplier and supplier account
- preflight state, exact sanitized failure reason, failure category, remediation, owner, and whether automatic push is enabled
- whether Codex issued a valid mutation, the sanitized mutation result, final push state, push time, and outsource order number
- success attribution, duplicate-submission guard, next action, sanitized evidence path, and privacy status

Store long numeric identifiers as text. Never write buyer name, buyer phone, delivery address, Cookie, token, authorization header, or request signature. A successful ERP state without an exact ledger readback is operationally incomplete.

## Known Failure Patterns

### Supplier balance insufficient

Meaning: the supplier-side distribution order cannot be paid. Recharge may trigger automatic retry. Re-query first after recharge.

### `tradeIdList` must not be null or empty

Meaning: request body was wrapped or sent under the wrong key. It did not create a supplier order. Fix the contract, but re-query before any retry because the automatic-push process may already have succeeded.

### Already processing or successful

Meaning: skip. Poll or report the existing final state. A second push risks duplication and provides no benefit.

### No matching order

Meaning: search all four states and additional pages. If still absent, stop and report that the platform order was not found; never substitute a title match.
