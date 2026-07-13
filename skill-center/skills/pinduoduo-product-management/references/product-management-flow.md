# Pinduoduo Product Management Flow

## Browser Control

Use `mcp__chrome_devtools`:

1. `list_pages`
2. `select_page` or `navigate_page`
3. `take_snapshot`
4. `click` / `fill` / `press_key`
5. `evaluate_script` only for bounded DOM inspection or when normal clicks fail
6. `list_network_requests` and `get_network_request` when the page state disagrees with the UI

On Windows, this flow still uses the same MCP tools rather than a PowerShell wrapper. When you need a manual reload, address-bar recovery, select-all, or browser-history navigation through `press_key`, use `Control+R` or `F5`, `Control+L`, `Control+A`, and `Alt+Left` / `Alt+Right`. If you save screenshots, evidence, exports, or copied attachments locally during the workflow, keep those filesystem paths quoted and in `C:/...` form.

## Contents

- List page and filters
- Row extraction
- Opening product details
- Product-detail field map
- Tested example
- Mutation and verification checklist

## List Page And Filters

Use `https://mms.pinduoduo.com/goods/goods_list?msfrom=mms_sidenav`. Confirm the banner shows the requested shop before any mutation. The route was validated with shop `百商好购` on 2026-07-13; treat that only as a tested example, not a default target.

Observed status tabs:

- `全部`
- `在售中(N)`
- `已下架(N)`
- `已售罄(N)`
- `发布中(N)`
- `已驳回(N)`
- `草稿箱(N)`

Observed query controls:

- `商品ID`: accepts multiple values separated by spaces or commas.
- `商品编码`: accepts multiple values separated by spaces or commas.
- `规格编码`: expects a complete SKU/specification code.
- `商品名称`: accepts name keywords.
- `查询`, `重置`, and `展开所有筛选项`.

Use semantic labels and snapshot UIDs. Do not depend on generated CSS class names because they include changing version suffixes.

## Row Extraction

Each visible row can expose:

- Product name, thumbnail, product ID, and product code.
- Price and `修改价格`.
- Total stock, `修改库存`, and low-stock state.
- Favorites, cumulative sales, and 30-day sales.
- Product health such as `健康商品` or `问题商品` with a pending-fix count.
- Created time and row state such as `销售中`.
- Actions such as `编辑`, `下架`, `商品数据`, `预览`, `二维码/链接`, and `发布相似品`.

The table header may also expose batch title, price, stock, tag-image, and publish/unpublish controls. Treat every batch action as a high-impact mutation and confirm its exact selected products and values immediately before use.

For a full-list request, compare the extracted row count with `共有 N 条`. Inspect pagination if the counts differ. Prefer a bounded read-only DOM function that returns row text/fields when the accessibility snapshot is too noisy.

## Opening Product Details

1. Locate the target row by product ID rather than title alone.
2. Take a verbose snapshot if `编辑` appears only as a `StaticText` node.
3. Find the row's ancestor `link "编辑"` UID and click that UID.
4. Call `list_pages`; the edit page commonly opens at `/goods/goods_add/index?...&goods_id=<ID>&type=edit` in a new tab.
5. Select the new page and take a fresh snapshot. Saving the snapshot to a temporary text file and searching labels with `rg` is useful for large forms.
6. Do not fill, toggle, upload, submit, or save during parameter inspection.
7. Close temporary or duplicate detail tabs and return to the original goods list after inspection.

## Product-Detail Field Map

Read labels together with textbox values, selected radios, checked boxes, and readonly fields.

`Identification`

- Product ID and product classification path.

`Basic information`

- Carousel image count and main image.
- Product title and title-length state.
- Attribute completion rate.
- Category-specific attributes such as brand, layers, quantity, dimensions, material, printing, usage scenario, customization, suspension, or grade.
- Product video, detail-image count, decorated detail, and white-background material.

`Specifications and inventory`

- Specification type, specification values, and specification images.
- Current stock, stock adjustment, resulting stock, group-buy price, single-buy price, specification code, and publish state.
- Total stock, product code, inventory-deduction method, reference price, quantity discount, and discounted price.

`Services and commitments`

- Product type, used/new state, customization, and presale state.
- Shipping and collection promise.
- Freight-template selection, free-shipping regions, paid-shipping regions, and excluded regions.
- Group size and mandatory/selected service promises.

Buttons `提交` and `保存草稿` are mutations. Merely reaching them does not authorize clicking them.

## Tested Example

The following values were observed only to validate the read path on 2026-07-13. Always re-read the live page.

- Product: `漫花大包抽纸气垫纸巾婴儿纸面巾纸整箱实惠家用餐巾纸批发卫生纸`
- Product ID: `972915600377`; product code: `C-LS280-6`; row state: `销售中`; health: `健康商品`.
- Category: `洗护清洁剂/卫生巾/纸/香薰 > 纸品/生活用纸 > 抽纸`.
- Brand `漫花`; 4 layers; 70 draws per pack; 30 packs; 170 x 140 mm; wood pulp; printed; home/commercial use; no customization; hangable; product grade blank.
- One specification: `加厚大包【6包/提】品质回购`; stock 500; group-buy price 9.89; single-buy price 71.87; specification code `C-LS280-6`; state `已上架`.
- Inventory deduction: after successful payment; reference price 93.42; two items at 9.9 discount; discounted group-buy price 9.79.
- Ordinary, non-used, non-custom, non-presale product; 48-hour shipping and collection; two-person group.
- Freight: `其他模板` using `偏远按件收费默认模板`; Hong Kong, Macau, and Taiwan excluded.
- Mandatory checked commitments shown: seven-day no-reason returns and counterfeit compensation.

## Mutation And Verification Checklist

Before changing data:

- Confirm shop, product ID, requested field, old value, new value, and whether the user authorizes final submission or only form preparation.
- For batch operations, enumerate the selected product IDs and total selection count.
- Keep unrelated fields untouched. Do not use AI title generation, recommended keywords, automatic specification generation, or campaign enrollment unless explicitly requested.
- Verify uploads show a preview or uploaded state before submission.

After an authorized submission:

- Check for confirmation dialogs, slider puzzles, CAPTCHA, or security verification before reporting success.
- If human verification appears, pause and ask the user to complete it; then inspect the final page again.
- Confirm the resulting value, publish state, review state, or visible success message.
- Report exactly what changed and what remained unchanged. If the platform did not provide a final state, report that uncertainty instead of claiming success.
