---
name: huice-product-media-export
description: Export exact Huice product media into a local folder for inspection or manual WeChat Store material preparation. Use for main images, detail images, and SKU images from a verified supplierGoodsId. Do not mutate business state.
---

# 慧策商品素材安全导出

Use the Huice HTTP API to read exact product detail media, then export main, detail, and SKU images to a dedicated local folder.

## Rules

- Verify supplier goods ID and shop context before downloading.
- Keep raw signed media URLs in memory only; never put them in manifests, cloud sheets, documents, or shared reports.
- Store only filename, kind, byte count, MIME type, SHA-256, and source IDs in `manifest.json`.
- Deduplicate by content hash and reject non-image responses.
- This workflow is read-only and never changes price, stock, publication, promotion, address, or task state.

## Output

```text
<output-dir>/main/...
<output-dir>/detail/...
<output-dir>/sku/...
<output-dir>/manifest.json
```

## Bundled helper

Use [`scripts/download-huice-detail-images.js`](scripts/download-huice-detail-images.js) to export an exact already-captured Huice detail JSON payload into a local folder without persisting signed URLs anywhere except in transient process memory.

```bash
node scripts/download-huice-detail-images.js \
  outputs/huice-detail.json \
  outputs/huice-media-export
```

## Windows Repo Mirror Notes

This skill keeps the same Node helper on Windows; it does not fork a second business implementation. When a Windows operator needs a local entry point, prefer the bundled PowerShell launcher [`scripts/download-huice-detail-images.ps1`](scripts/download-huice-detail-images.ps1) instead of rewriting the command into ad hoc `cmd.exe` syntax.

```powershell
.\scripts\download-huice-detail-images.ps1 `
  "C:/Users/<name>/Downloads/huice-detail.json" `
  "C:/Users/<name>/Downloads/huice-media-export"
```

When a browser or file picker step needs keyboard recovery through `press_key`, prefer Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\huice-product-media-export\\`. Keep exported JSON inputs, output folders, and evidence paths quoted and in `C:/Users/<name>/...` form instead of `/Users/...`.
