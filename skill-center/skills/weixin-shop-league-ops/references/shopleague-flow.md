# 微信小店优选联盟操作参考

## Scope And Safety

Use this reference for live work in 微信小店优选联盟. Keep all business mutations inside the visible merchant UI. Use page text and current UI state as the source of truth when they differ from previously observed routes or response fields.

Never persist or quote request headers that contain cookies, tokens, signatures, magic values, authorization data, QR payloads, or device identifiers. When network inspection is necessary, record only the minimum non-sensitive response fields needed to explain business state.

Do not infer the meaning of undocumented numeric status codes. Find the matching visible UI label or report the code as unresolved.

## Windows Notes

The workflow remains browser-based on Windows through `mcp__chrome_devtools`; it needs no platform-specific command wrapper. For manual browser recovery use `Control+R` or `F5` (reload), `Control+L` (address bar), `Control+A` (select all), and `Alt+Left` / `Alt+Right` (history). Quote any locally saved evidence or export path, for example `"C:/Users/<name>/Downloads/alliance-audit.csv"`.

## Browser Sequence

Use `mcp__chrome_devtools` in this order:

1. Run `list_pages` and select the existing logged-in merchant tab when available.
2. Navigate to the requested route or open a clean new tab.
3. Run `take_snapshot` to obtain current element identifiers.
4. Use `take_screenshot` when the main content, dense table, modal, loading state, or visual status is unclear.
5. Use `click`, `fill`, `fill_form`, and `press_key` only with current snapshot identifiers.
6. Use bounded `evaluate_script` reads when snapshot text is incomplete. Do not run scripts that submit forms, invoke private mutation APIs, or circumvent controls.
7. Use console and network inspection only for diagnosis or state verification.
8. Close diagnostic duplicate tabs after the workflow is complete.

Verify the visible store name before preparing a mutation. Stop for login or security challenges.

## Route Map

Use the full origin `https://store.weixin.qq.com` with these observed paths:

| Module | Route | Purpose |
| --- | --- | --- |
| 带货者推广 | `/shop/shopleague/home` | View promotion plans and alliance state |
| 新建普通推广 | `/shop/shopleague/home/normal-add` | Prepare a normal/public promotion plan |
| 新建定向推广 | `/shop/shopleague/home/promote-add` | Prepare a targeted promotion plan |
| 机构推广 | `/shop/shopleague/head-supplier` | Search, review, and invite institutions |
| 活动推广 | `/shop/shopleague/event-promotion` | Review and apply for platform activities |
| 合作管理 | `/shop/shopleague/coop-manage` | Review current cooperation relationships |
| 机构黑名单 | `/shop/shopleague/coop-manage/blacklist` | Review institution blacklist state |
| 带货者黑名单 | `/shop/shopleague/coop-manage/promoter-blacklist` | Review promoter blacklist state |
| 合作时效管理 | `/shop/shopleague/coop-manage/timeManagement` | Review expiry and renewal state |
| 联盟规则 | `/shop/shopleague/league-rule` | Review current rules and notices |
| 联盟数据入口 | `/shop/shopleague/contact-info` | Observed navigation mapping; verify the page title before relying on it |

Other sidebar entries can route outside `/shop/shopleague`, including 专属营销、达人广场 and 机构广场. Prefer clicking the current sidebar entry over guessing a route.

## Read-Only Audit

Complete the relevant checks before making a recommendation or preparing a form:

- Confirm the shop name, login state, and whether 优选联盟 is open.
- Read the current alliance rule state and any clearance, violation, or eligibility warning in visible UI wording.
- List active, scheduled, expired, and draft promotion plans.
- For each candidate product, capture product name, product ID, sales state, price, inventory, refund signal, existing commission, plan membership, and eligibility warning.
- Review current promoter and institution relationships, including type, commission, start time, expiry, and status.
- Review pending invitations, applications, audits, renewals, and terminations.
- List open platform activities with application deadline, activity period, product price rule, inventory requirement, audit requirement, and visible eligibility result.
- Read alliance data for exposure, clicks, orders, GMV, commission, refunds, partner contribution, and product contribution when available.
- Compare displayed figures using the same time range. Label unavailable metrics instead of estimating them.

For tables without an export control, extract only visible business rows into a local Markdown or CSV artifact when the user requested an export. Do not capture request headers or hidden credentials.

## Decision Order

Use this order when planning alliance operations:

1. Fix blocked products, expired relationships, and rule warnings.
2. Select products that can support commission after cost, logistics, platform fees, discounts, and after-sales reserve.
3. Create a small candidate pool before expanding product count.
4. Test public promotion on broadly suitable products and targeted promotion for specific partners or negotiated terms.
5. Invite institutions only after identity, category fit, conditions, and expected economics are verified.
6. Join platform activities only when the activity price and stock obligation remain profitable and operationally supportable.
7. Review results by product and partner before increasing commission, inventory exposure, or scope.

Use this contribution-margin check before recommending a commission:

`可承受佣金 = 实付价 - 货源成本 - 物流/履约成本 - 平台费用 - 优惠分摊 - 售后准备金 - 最低目标利润`

Obtain actual current values from the merchant backend or supplier source. Do not invent a commission rate when cost or fee inputs are missing. If the backend expresses commission as a rate, convert the amount to a rate against the same expected paid price and leave a conservative buffer.

## 带货者推广 SOP

1. Read existing promotion plans and exclude duplicated, expired, ineligible, out-of-stock, or high-refund products.
2. Build a candidate list using current sales, refund, inventory, price, gross margin, category qualification, and delivery stability.
3. Choose the plan type from the current UI:
   - Use normal/public promotion for products suitable for broad distribution with standardized terms.
   - Use targeted promotion when a named promoter, negotiated commission, limited scope, or fixed period is required.
4. Start with 5-10 qualified products unless the user specifies a smaller exact set.
5. Calculate a proposed commission range from contribution margin. Preserve minimum target profit and after-sales reserve.
6. Set a short test period when the UI supports an expiry. Use current stock and supplier stability to cap scope.
7. Prepare the plan and stop before the final create, publish, save-effective, or confirm action.
8. Present the exact product IDs, prices, commission rates, scope, and dates for confirmation.
9. After explicit confirmation, submit through the UI and verify each product's plan status.
10. Reassess after a consistent observation window, normally 7 days or enough orders to make refund and conversion signals meaningful.

For `百亿好购店`, use these dated observations only as starting hypotheses:

- On 2026-07-09, `牙博士幻海羽柔软毛牙刷` (product ID `10001092885450`, displayed price `¥6.43`) had one observed transaction and no observed refund. Recheck current data before selecting it.
- On 2026-07-09, a sun-protection mask (product ID `10001088838759`, displayed price `¥9.20`) had a full observed refund and was taken down. Exclude it unless newer evidence reverses the risk.
- Treat dental floss and selected snack products as candidate categories, not proven winners. Verify current listing, margin, stock, qualification, and refund data first.
- Keep AI采购小鲸灵 supplier cost and fulfillment stability in the margin calculation when it remains the active source.

## 机构推广 SOP

1. Search the institution by exact name or identifier in 机构推广 or 机构广场.
2. Verify the entity shown by the platform, its category fit, cooperation status, visible track record, requested terms, contact path, and any warning.
3. Compare the institution's requested commission and service conditions with product contribution margin.
4. Check for duplicate invitations, existing cooperation, exclusivity, expiry, or blacklist conflicts.
5. Create a shortlist with reasons, suitable products, proposed terms, test duration, and stop conditions.
6. Prepare one institution invitation at a time unless the user explicitly approves a named batch.
7. Stop before the final invite or confirm action. Present the institution, products, commission, period, exclusivity, and obligations for confirmation.
8. After explicit confirmation, submit and verify invitation status in 合作管理.

Do not send blind bulk invitations. Do not infer identity from a similar display name.

## 活动推广 SOP

1. Open 活动推广 and refresh the current activity list.
2. Read the activity name, application deadline, activity period, merchant eligibility, product eligibility, price rule, stock requirement, audit requirement, protocol, and exit condition.
3. Reconcile the required activity price against recent selling price, supplier cost, commission, discounts, platform fees, and minimum profit.
4. Exclude products with unstable stock, unresolved review issues, qualification gaps, or excessive refund risk.
5. Prepare the candidate products and activity fields, then stop before the final apply or submit action.
6. Present the activity, product IDs, submitted prices, committed stock, audit implications, and deadline for confirmation.
7. After explicit confirmation, submit and verify whether each product is pending audit, accepted, rejected, or requires correction.

Historical observation from 2026-07-10, for orientation only:

- `微信小店入夏好物活动` was shown as shop-applicable, with application deadline `2026-07-20 23:59:59` and activity end `2026-07-21 12:00:00`.
- The observed response indicated price checks against recent and selling prices and required platform review.
- Re-read the live page before acting. Do not use this dated observation as proof of current eligibility or availability.

## 合作管理 SOP

1. Read all visible cooperation, pending invitation, expiry, and blacklist states.
2. Export through the UI when available. Otherwise extract the visible rows requested by the user.
3. Group relationships into active, expiring, expired, pending, underperforming, duplicated, and risk-flagged.
4. Compare partner contribution, commission cost, refund rate, and order quality over the same time range.
5. Recommend keep, renew, adjust, pause, end, or blacklist with evidence and a stated consequence.
6. Prepare only the user-approved scope and stop before the final mutation.
7. For renewals or adjustments, present the old and new terms, effective date, and affected products.
8. For termination or blacklist actions, present the exact entity, reason, downstream effect, and reversibility.
9. After explicit confirmation, submit and verify the resulting relationship and blacklist state.

Never use blacklist as a substitute for weak performance management; reserve it for documented risk or clear policy reasons.

## 达人广场、机构广场、专属营销

Use the squares for discovery and read-only shortlisting. Capture exact platform identity, category fit, visible performance evidence, cooperation terms, and existing relationship. Move to the corresponding promotion or cooperation workflow before inviting or creating a plan.

Use 专属营销 only for a named counterpart and explicit commercial terms. Treat its creation, modification, or deletion as a mutation requiring action-time confirmation.

## 联盟规则与联盟数据

Read current rules before changing a plan or relationship. Surface rule changes, eligibility warnings, clearance risk, price constraints, prohibited behavior, and unresolved platform notices in visible UI wording.

Use alliance data to answer e-commerce operating questions by product and partner. Prioritize:

- Paid orders and GMV
- Product and partner conversion
- Refund amount and refund rate
- Commission amount and commission-to-GMV ratio
- Net contribution after commission and after-sales cost
- Inventory and fulfillment constraints

Do not recommend paid traffic from alliance data alone. Do not add short-video or livestream tasks unless requested.

## Confirmation Gate

Use this compact confirmation message before any mutation:

```text
待确认操作：<创建/修改/报名/邀请/续期/解除/拉黑/关闭/修改联系方式>
对象：<商品ID、计划名、活动名、达人或机构准确名称>
商业条件：<价格、佣金、库存、有效期、合作范围>
影响：<生效方式、审核、费用、合作或下架风险>
我已停在最终提交前。请确认是否按以上内容提交。
```

Do not combine materially different actions into one confirmation. For example, confirm activity enrollment separately from institution invitations.

## Blank Page Recovery

When the 优选联盟 micro-application is blank or fails to load:

1. Capture a screenshot and read `document.readyState`, URL, main text, iframes, and `micro-app` state with a bounded DOM inspection.
2. Inspect console errors for chunk-load, script, syntax, or micro-application errors.
3. Inspect document, script, stylesheet, fetch, and XHR requests. Identify failed or pending critical resources without copying sensitive request headers.
4. Press Escape if loading is hung, then perform a normal reload or open the same route in a clean new tab.
5. Retry with cache disabled only through normal DevTools behavior; do not alter production data.
6. Use SSR HTML and public static route metadata only to identify routes or labels when rendering remains broken.
7. Do not treat static route discovery or undocumented response codes as proof that a business action succeeded.
8. Stop and report the rendering failure if current UI state cannot be verified safely.

## Result Report

Report these items after each run:

- Shop and module inspected
- Time range and source of evidence
- Current alliance, plan, product, activity, or cooperation state
- Recommendation or exact action performed
- Confirmation received for each mutation
- Post-action verification result
- Items not changed and any remaining blocker

For read-only runs, state explicitly that no promotion, commission, activity application, invitation, cooperation, blacklist, rule, or contact data was changed.
