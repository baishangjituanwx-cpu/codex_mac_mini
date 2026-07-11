# 微信小店商品列表检查流程

## Entry And State Verification

Use `https://store.weixin.qq.com/shop/goods/list` as the base route. A shared link can include parameters such as:

`?currentTab=PRODUCT_STATUS_CHECK_FAIL&currentPage=1`

Treat query parameters as navigation hints, not authoritative state. In the observed frontend, clicking `销售中` changed the table to 23 selling products while the URL still contained `currentTab=PRODUCT_STATUS_CHECK_FAIL`. Verify the selected dataset with all three signals:

1. The requested tab count, such as `销售中 23`.
2. The table total, such as `共23条`.
3. The visible row status, such as `销售中` on each row.

Do not guess undocumented `currentTab` enum values. Prefer clicking the visible tab.

## Chrome DevTools MCP Sequence

1. Run `list_pages`.
2. Select the logged-in merchant page or navigate the selected page to the requested URL.
3. Run `take_snapshot` before every click.
4. Capture a screenshot when the active tab, loading state, table, modal, or pagination is visually unclear.
5. Click the requested tab and wait for the displayed table total to change.
6. Use bounded `evaluate_script` reads only when the snapshot is stale or the table is inside the `micro-app` shadow root.
7. Use console and network inspection only when the page fails to load or the UI state cannot be verified.
8. Never copy sensitive request headers into a report or skill.

If the MCP reports that the automation profile is already running, inspect the related processes first. Restart only the dedicated `chrome-devtools-mcp/chrome-profile` browser after determining that it is stale or contested; do not terminate the user's ordinary Chrome profile.

On Windows, this flow still uses the same MCP tools rather than a PowerShell wrapper. When you need a manual reload, address-bar recovery, select-all, or browser-history navigation through `press_key`, use `Control+R` or `F5`, `Control+L`, `Control+A`, and `Alt+Left` / `Alt+Right`. If you save screenshots, evidence, exports, or copied attachments locally during the workflow, keep those filesystem paths quoted and in `C:/...` form.

## Store Overview

Capture these tab counts exactly as displayed:

- 全部
- 销售中
- 已下架
- 审核中
- 审核待处理
- 草稿箱
- 回收站

Do not assume the counts are mutually exclusive business totals. Report the labels and numbers without deriving unsupported reconciliation.

## Row Fields

Extract fields that are visible in the current tab:

- 商品名称
- 商品 ID
- 规格/编码 availability
- 商品价格
- 总库存
- 待付款库存
- 近30天销量
- 历史累计销量
- 曝光 and 平台推荐 count
- 信息待调整 count or other health message
- 商品状态
- 上架策略状态
- 创建、上架、下架, or draft time
- Available row actions

Do not interpret `信息待调整 N` as N rejected reviews. Preserve the exact label and count.

## Visible-Row Extractor

Use the latest snapshot first. When it contains stale rows after a page switch, run this bounded read inside the current page:

```js
() => {
  const root = document.querySelector("micro-app")?.shadowRoot;
  if (!root) return { error: "no micro-app shadow root" };

  const visible = (el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };

  const idElements = [...root.querySelectorAll("*")].filter((el) =>
    /^ID:\s*\d+$/.test((el.innerText || "").trim()) && visible(el)
  );

  return idElements.map((idElement) => {
    let row = idElement;
    for (let i = 0; i < 8 && row?.parentElement; i += 1) {
      row = row.parentElement;
      const text = (row.innerText || "").trim();
      const hasPrice = /￥\s*\d/.test(text);
      const hasState = /(销售中|已下架|审核未通过|审核中|待发布)/.test(text);
      if (hasPrice && hasState) break;
    }

    const text = (row?.innerText || "").replace(/\s+/g, " ").trim();
    const match = (pattern) => text.match(pattern)?.[1] ?? null;
    const status = ["审核未通过", "审核中", "已下架", "销售中", "待发布"]
      .find((value) => text.includes(value)) ?? null;

    return {
      name: text.split(/\s+ID:/)[0] || null,
      id: match(/ID:\s*(\d+)/),
      price: match(/￥\s*([\d.]+)/),
      stock: match(/￥\s*[\d.]+\s+(\d+)/),
      pendingStock: match(/待付款库存\s*(\d+)/),
      recentSales: match(/销量\s*(\d+)/),
      historicalSales: match(/历史累计\s*(\d+)/),
      exposure: match(/曝光\s*(\d+)/),
      platformRecommendations: match(/平台推荐\s*(\d+)/),
      informationAdjustmentCount: match(/信息待调整\s*(\d+)/),
      status,
      listingStrategyActive: text.includes("上架策略生效中"),
      listedAt: match(/上架时间:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})/),
      rowText: text,
    };
  });
}
```

Keep `rowText` during extraction so ambiguous parsed fields can be checked against the exact visible wording. Remove it from the final report when the structured fields are sufficient.

## Pagination

1. Record the current page's first visible product ID and all extracted IDs.
2. Click `下一页` or the next page number using the latest snapshot.
3. Wait until the visible first product ID changes. URL changes alone are insufficient.
4. Extract only visible ID elements. Hidden or stale accessibility nodes can contain the prior page.
5. Repeat until `下一页` is absent/disabled or the page yields no new IDs.
6. Deduplicate by product ID.
7. Compare the unique ID count with `共N条`.

For a 23-row result at 20 rows per page, require 20 unique rows on page 1 and 3 unique rows on page 2.

## Review-Failure Inspection

For 审核待处理 or 审核未通过:

1. Capture product name, ID, price, stock, draft time, status, and available actions.
2. Click the status detail only to read the rejection reason when the user asks for it.
3. Do not click 编辑, 删除, 隐藏, 复制, 发布, or resubmit without action-time confirmation.
4. Report the platform's reason verbatim only when short; otherwise summarize it accurately.
5. Separate qualification/category failures from title, image, attribute, price, or content failures.

## Loading Recovery

If the product table is blank or stuck:

1. Read `document.readyState`, current URL, `micro-app` presence, and visible text.
2. Take a screenshot.
3. Inspect console errors.
4. Inspect document, script, stylesheet, fetch, and XHR statuses.
5. Press Escape for a hung load, then reload or open a clean tab.
6. Verify data from current visible UI before reporting success.

## Mutation Gate

Require explicit confirmation at the final action for:

- 编辑 or 免审编辑
- Price or stock changes
- Publish, list, delist, hide, restore, or delete
- Copying a product into a new listing
- Content-management changes
- Evaluation-campaign creation
- Any batch operation

Use this confirmation format:

```text
待确认操作：<操作名称>
商品：<名称与商品ID>
变化：<旧值 -> 新值，或状态变化>
范围：<单品或明确的批量商品ID>
影响：<审核、销售、库存或展示影响>
我已停在最终提交前。请确认是否执行。
```

## Report Format

Report:

1. Store name, inspection date, requested tab, and source URL.
2. All tab counts.
3. Extracted row count and pagination completeness.
4. A product table with the requested fields.
5. Exceptions: health warnings, duplicate titles, low stock, strategy-controlled products, and nonzero performance signals.
6. A statement that no merchant data changed during read-only work.
