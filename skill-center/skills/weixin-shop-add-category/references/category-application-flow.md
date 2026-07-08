# 微信小店类目申请操作细节

## Browser Control

Use `mcp__chrome_devtools`:

1. `list_pages`
2. `select_page` or `navigate_page`
3. `take_snapshot`
4. `click` / `fill` / `press_key`
5. `evaluate_script` only for bounded DOM inspection or when normal clicks fail
6. `list_network_requests` and `get_network_request` when the page state disagrees with the UI

The category pages are rendered inside a `micro-app` shadow root. Snapshot `uid` clicks usually work, but buttons and result rows can sometimes require an `evaluate_script` click inside:

```js
const root = document.querySelector("micro-app")?.shadowRoot;
```

On Windows, this flow still uses the same MCP tools rather than a PowerShell wrapper. When you need a manual reload or location-bar recovery through `press_key`, use `Control+R` or `F5`, `Control+L`, and `Alt+Left` / `Alt+Right`. If you save screenshots, evidence, or copied attachments locally during the workflow, keep those filesystem paths quoted and in `C:/...` form.

## Entry Points

- Category home: `https://store.weixin.qq.com/shop/brandAndCat/category/home`
- Apply page usually opens as: `/shop/brandAndCat/category/apply?isShowCategorySearchModel=true`

Clicking `申请新类目` can open duplicate tabs. Keep the latest apply tab selected, and close duplicates after the flow succeeds.

## Selecting A Category

In the category selection modal:

1. Fill the search input with a keyword such as `休闲零食`.
2. Press `Enter`.
3. Choose the exact path, then click `确认`.

For leisure snacks, useful leaf paths are:

- `食品饮料 > 休闲食品 > 休闲零食 > 其它零食`
- `食品饮料 > 休闲食品 > 休闲零食 > 膨化食品`
- `食品饮料 > 休闲食品 > 休闲零食 > 豆干/素食零食`
- `食品饮料 > 休闲食品 > 休闲零食 > 海味零食`
- `食品饮料 > 休闲食品 > 休闲零食 > 蛋类零食`

When a search result row will not select through the normal MCP click, use a bounded row click:

```js
const root = document.querySelector("micro-app")?.shadowRoot;
const target = "食品饮料休闲食品休闲零食其它零食";
const row = [...root.querySelectorAll(".search_content_item")]
  .find((el) => (el.innerText || el.textContent || "").replace(/\s+/g, "").trim() === target);
if (!row) throw new Error("category row not found");
row.scrollIntoView({ block: "center", inline: "center" });
const r = row.getBoundingClientRect();
const opts = {
  bubbles: true,
  cancelable: true,
  composed: true,
  view: window,
  clientX: r.left + r.width / 2,
  clientY: r.top + r.height / 2,
  button: 0,
  buttons: 1,
};
for (const type of ["pointerover", "mouseover", "pointerdown", "mousedown", "pointerup", "mouseup", "click"]) {
  row.dispatchEvent(new MouseEvent(type, opts));
}
row.click();
```

If search-row selection does not update the modal selection, clear the search or use the visible category tree, expand `食品饮料 > 休闲食品 > 休闲零食`, then click the leaf text via snapshot `uid`.

## Qualification

After confirming the category:

1. Review the guarantee deposit and category path.
2. Select the required qualification type.
3. For food categories that accept prepackaged-food filing, select `《预包装食品销售备案凭证》`.
4. If the page shows `已复用证照`, verify the visible filing number, query link, validity, and image/attachment state. Reuse the existing credential unless the user says to upload or change materials.

Do not invent credential numbers, links, or attachments.

## Submitting

Before clicking `提交审核`, confirm the exact submission with the user unless their latest message already explicitly authorizes it.

If the normal MCP click focuses but does not trigger the button, click the shadow-DOM button by exact text:

```js
const root = document.querySelector("micro-app")?.shadowRoot;
const btn = [...root.querySelectorAll("button")]
  .find((el) => (el.innerText || el.textContent || "").trim() === "提交审核");
if (!btn) throw new Error("submit button not found");
btn.scrollIntoView({ block: "center", inline: "center" });
const r = btn.getBoundingClientRect();
const opts = {
  bubbles: true,
  cancelable: true,
  composed: true,
  view: window,
  clientX: r.left + r.width / 2,
  clientY: r.top + r.height / 2,
  button: 0,
  buttons: 1,
};
for (const type of ["pointerover", "mouseover", "pointerdown", "mousedown", "pointerup", "mouseup", "click"]) {
  btn.dispatchEvent(new MouseEvent(type, opts));
}
btn.click();
```

## Batch Prompt

The backend may show a prompt like:

`「某类目」类目申请通过后，可同时为你开通以下N个类目权限，是否批量申请？`

Use the prompt's listed categories as the source of truth.

- Click `确认申请` only when the user asked to batch apply the listed categories.
- Click `仅申请当前类目` only when the user wants the selected category alone.
- Ask if the categories differ from the user's request.

## Verification

After submission, return to category home and verify:

1. `生效中` and `审核中` tab counts.
2. Category rows contain the requested leaf names.
3. Effective rows usually show actions such as `更新资质`, `发布商品`, and `删除类目`.
4. If the UI shows stale `审核中` state, reload the page and optionally inspect `getCategoryAuditList` network responses.

Report the final state category by category: effective, pending review, failed, or not found.
