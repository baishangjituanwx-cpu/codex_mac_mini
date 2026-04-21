# Docker Dashboard Contract

Use this reference when the review output must feed the 8-platform Docker dashboard that currently renders a static `board` object plus a `platforms` array.

The review is still the source of truth. This contract only defines the exact fields the dashboard needs.

## Output shape

Return one appendix block named `Docker 看板数据映射`.

When the workflow writes files for deployment, it may also save the exact same object as a companion JSON export next to the review log.
In that case, section 9 of the review should explicitly record the companion JSON file path.

That appendix or companion JSON must provide:

- one `board` object
- one `platforms` array with exactly 8 items
- optional `footerLinks` only when the source files really exist

## Board object

Required fields:

- `title`
- `dateLabel`
- `subtitle`
- `northStar`
- `summary`
- `keep`
- `cut`
- `next`

Rules:

- `summary` must contain exactly 4 tiles.
- Every summary tile must include:
- `label`
- `value`
- `note`
- `tone`
- `tone` must be one of: `cool`, `steady`, `warning`, `hot`
- `keep`, `cut`, and `next` must each contain exactly 3 items.
- `dateLabel` must use an absolute date, for example `2026-04-21 最新已确认数据`.
- `subtitle` should explain the current baseline and what newer evidence has been merged.
- `northStar` should stay short enough to fit in one line on desktop.

Preferred summary-tile roles:

1. confirmed sample coverage
2. strongest confirmed sample
3. biggest current blocker or quality risk
4. next main topic or main judgment

## Platforms array

The dashboard currently expects exactly these 8 keys and display names:

1. `kuaishou` / `快手`
2. `wechat` / `视频号`
3. `weibo` / `微博`
4. `toutiao` / `头条号`
5. `baijiahao` / `百家号`
6. `douyin` / `抖音`
7. `bilibili` / `B站`
8. `zhihu` / `知乎`

Every platform item must include:

- `key`
- `name`
- `status`
- `statusLabel`
- `latestTitle`
- `publishTime`
- `contentType`
- `primaryLabel`
- `primaryValue`
- `compareLabel`
- `baselineValue`
- `baselineNote`
- `windows`
- `metrics`
- `diagnosis`
- `action`

## Platform field rules

### Status

- `status` must be one of: `steady`, `watch`, `warning`, `weak`, `opportunity`
- `statusLabel` is the Chinese display label shown on the card
- Choose the status from verified evidence, not from aesthetic balance

Suggested meaning:

- `steady`: current evidence is relatively stable or clearly usable
- `watch`: data exists but still needs more observation
- `warning`: a concrete blocker exists and should be highlighted
- `weak`: current confirmed signal is clearly weak
- `opportunity`: the platform or format shows directional upside worth leaning into

### Primary metric

- `primaryValue` must be numeric
- If no confirmed numeric value exists yet, use `0`
- `primaryLabel` must be the visible metric label that the card is ranking on
- The dashboard sorts and renders ring sizes from `primaryValue`, so never use `-` here

### Comparison baseline

- `compareLabel` names the comparison dimension, for example `上一条方法视频` or `文章阅读`
- `baselineValue` may be numeric or a short string, but numeric is preferred when possible
- `baselineNote` explains the time window, fallback logic, or pending-review state

### Windows

- `windows` must contain exactly 3 items in this order:
1. `今日`
2. `近7日账号`
3. `近30日账号`
- Every window must include:
- `label`
- `headline`
- `metrics`
- `metrics` should follow the dashboard's compact account-metric vocabulary where possible:
  - `播放量`
  - `主页访问`
  - `作品点赞`
  - `作品分享`
  - `作品评论`
  - `封面点击率`
  - `净增粉丝`
  - `取关粉丝`
  - `总粉丝量`
- If a metric is not visible, keep the slot and use `-`
- If the whole window is not visible, still provide the window and set `headline` to `-`

### Compact metrics

- `metrics` must contain exactly 4 items
- Every compact metric item must include:
- `label`
- `value`
- Prefer the 4 most decision-relevant visible numbers or states for that platform
- Use short labels that fit on the card

### Text fields

- `latestTitle` should be the verified current work title, or a precise identifier if no title is visible
- `publishTime` should compress publish date, state, and any fallback note into one short line
- `contentType` should be short, for example `视频`, `图文`, `视频 + 文章`
- `diagnosis` should be one short paragraph grounded in evidence
- `action` should be one short paragraph that names the next action, not a vague wish

## User-facing display rules

- The dashboard is a user-facing screen, not an internal scratchpad.
- Never output unlabeled packed number strings such as `86 / 0 / 0 / 0 / 0`, `337 / 8`, or `3 / 1 / 0` into any user-facing display field.
- Every displayed number must carry a field name in the same string or in the same label-value cell.
- If the platform page does not reveal a field name, explicitly mark it as `未命名列2`, `未命名列3`, and so on.
- `headline`, `baselineNote`, and every compact `metrics[].value` must read like something a non-author can understand without prior context.
- Short date labels such as `04-20` can appear only as supporting context. They are not sufficient metric labels by themselves.

## Missing-data handling

- Never omit a platform because data is missing.
- If a platform was planned but not found, keep the card and say so.
- If only the entry page was checked, write `未完成内容级核验` in the review and reflect that limit in the card text.
- Use `0` only for numeric fields that the dashboard computes with, especially `primaryValue`.
- Use `-` for non-numeric missing display values.
- If a platform is paused or this batch has no platform data, keep the card and set its missing display fields to `-` while leaving `primaryValue` as numeric `0`.

## Footer links

`footerLinks` are optional for the contract.

Only output them when the referenced files really exist at deploy time. Otherwise, keep the dashboard's current links unchanged or omit the field from the appendix.
