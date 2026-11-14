---
name: weixin-shop-material-copy
description: Configure, validate, and verify Chinese delivery copy for every WeChat Store paid-traffic material after upload. Use when uploading a video or image to 小店投放, auditing material rows, repairing missing 配置投放文案, or confirming that copy changes and review status were recorded for an exact task, product, and material ID.
---

# 微信小店素材文案闭环

Use `chrome-devtools-mcp` on the official WeChat Store console. Treat the live page as authoritative for material IDs, copy fields, review status, and button behavior.

## Mandatory completion rule

Never mark an upload workflow complete until the exact new material row has all of:

- exact task ID and product `platformGoodsId` resolved;
- material filename and material ID recorded;
- material type, source, upload time, and review status read back;
- `投放文案` visibly populated with a deliberate Chinese copy;
- post-save readback confirms the same copy on the same material row.

If the material is still `审核中`, keep that state. Do not describe it as approved, enabled, or delivering.

## Workflow

1. Open the exact 小店投放 detail page and verify the task ID and product ID from the live page.
2. Upload through the live `添加素材` page. If the upload fails, stop the material flow and report the exact page error; do not configure copy for a material that was not accepted.
3. After upload succeeds, locate the new row by exact filename and material ID, never by row order alone.
4. Inspect the row's operation control. If it says `配置投放文案`, the copy is missing and must be configured before completion. If it shows existing `投放文案`, read it back and only change it when the user asks or when it is clearly unsuitable.
5. Use a copy based only on verified product facts. Prefer this structure: product name or category + one or two visible selling points + a restrained click prompt.
6. Submit the copy. If the console warns that changing copy triggers re-review or temporarily stops delivery, acknowledge the warning only as part of the current user-authorized material operation.
7. Re-read the row after the dialog closes. Confirm the exact copy, material ID, and review status. Capture a screenshot or structured page evidence when useful, but never save cookies, tokens, signed URLs, or credentials.

## Copy rules

- Write visible copy in Chinese; keep IDs, filenames, and system status labels exactly as shown by the platform.
- Use only facts visible in the material or verified from the exact product record.
- Do not invent price, discount, stock, sales volume, certification, medical effect, safety guarantee, ranking, absolute claim, or delivery promise.
- Avoid keyword stuffing. Keep the copy concise, natural, and suitable for a product-card click.
- The console suggests at least 10 characters; follow the live character limit and validation message rather than hard-coding a universal limit.
- For the dental-brush product `10001252850579`, an approved factual pattern is: `牙博士宽密软毛牙刷，家庭十支装，三种配色，点击查看详情`.

## State and audit rules

- `审核中` means uploaded and under review only.
- A copy edit may return a previously approved material to `审核中`; record that transition instead of treating it as an upload failure.
- Query the current row after save, not only the success toast.
- If the row cannot be matched exactly, do not edit a nearby material or infer the ID from position.
- When several materials are uploaded in one task, process and verify each material independently.
- Keep the operation log and cloud-sheet checkpoint consistent with the exact material ID, copy, timestamp, and review status when the surrounding workflow requires logging.

## Tool discipline

- Use `take_snapshot` before clicking and use fresh UIDs after every modal or page change.
- Use `evaluate_script` only for bounded DOM inspection such as locating the exact material row; use normal snapshot/click/fill tools for mutations.
- Before a mutation, confirm the exact target row and current value at action time.
- Do not use unofficial API calls, guessed endpoints, browser cookies, tokens, request signatures, or stored login data.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` workflow inside Codex, so the repo mirror stays shared instead of forking browser or shell wrappers.

When a browser interaction needs keyboard input through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back and forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-material-copy\\`. Keep local screenshots, structured evidence, exported logs, and copied attachments quoted and in `C:/Users/<name>/...` form instead of `/Users/...`. Do not save cookies, tokens, signed URLs, or credentials in those files.
