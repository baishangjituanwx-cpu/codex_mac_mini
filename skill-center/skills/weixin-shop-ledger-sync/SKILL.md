---
name: weixin-shop-ledger-sync
description: Write and verify WeChat Store, Huice, supplier-change, price-floor, publication-recovery, promotion, and process-review evidence into Feishu sheets and documents.
---

# 微信小店云台账与流程复盘同步

Cloud-record mechanics only. Product safety and publication decisions stay with the owning workflow.

## Rules

- Use `lark-cli sheets` and `lark-cli docs`; write the smallest exact range and read it back.
- Preserve all IDs as text. A missing required field, EOF, or failed readback keeps the event pending.
- Every review must distinguish the review cutoff from the latest live official capture; heartbeats are not live-state evidence.
- Keep `COMPLIANT`, `BELOW_CONTROL_MIN_PRICE`, `MARGIN_FAIL`, `SUPPLIER_STOPPED_LIVE`, `ADDRESS_INCOMPLETE_NO_WRITE`, `MAPPING_INCOMPLETE_NO_WRITE`, `REVIEWING_NOT_HARD_SUCCESS`, `ISOLATED_DUPLICATE_CONTAINED`, and `RECOVERED_HARD_SUCCESS` distinct.
- Do not append a duplicate order row when the exact order/trade row already exists.
- Never write or output tokens, cookies, signatures, login credentials, or buyer privacy.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` wrapper. The same `lark-cli sheets` and `lark-cli docs` flow remains the Windows-usable equivalent, so the repo mirror should stay shared rather than fork cloud-write scripts by platform.

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-ledger-sync\\`. Any local Markdown backup, evidence path, or exported readback file should use quoted `C:/Users/<name>/...` absolute paths instead of `/Users/...`.

When invoking a helper command from PowerShell, keep sheet names, document keywords, IDs, and cell ranges quoted so they stay text rather than being coerced by the shell or spreadsheet layer.

## Handoffs

Price decisions go to `weixin-shop-price-floor-audit`; exact listing recovery goes to `weixin-shop-publish-recovery`; orders and activities remain separate skills.
