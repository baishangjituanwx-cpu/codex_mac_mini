---
name: weixin-shop-audience-targeting
description: 优化微信小店「小店投放/商品托管」的人群倾向。用于按指定投放时间范围读取累计曝光排名、进入精确商品详情、结合商品属性提出性别/年龄/城市的受控收窄假设、保存并官方回读人群设置，以及根据曝光、点击、加购和成交数据继续收窄、回扩或回滚。不得把无数据的设置说成已验证结论，也不得误改投放形象、预算、ROI、素材或投放状态。
---

# 微信小店人群倾向优化

## 核心目标

将人群倾向当作可回读的投放实验变量。先用商品属性形成垂直但可解释的初始假设，再用官方投放数据验证转化，不以“全部不限”作为默认完成态，也不把一次保存当成效果证明。

## 固定边界

- 只在微信小店官方后台操作人群倾向；使用 `weixin-shop-goods-inspection` 与 `chrome-devtools-mcp` 做精确商品 ID、当前投放状态和详情回读。
- 每轮先刷新官方小店投放商品列表，并在同一次登录会话内读取排名、分页、商品详情和保存后的设置。
- 慧策域只确认登录上下文、刷新临时认证或核对请求契约；不得用浏览器业务按钮修改慧策商品。
- 不保存或输出 Cookie、token、magic 值、请求签名、登录凭据、买家隐私或明文手机号。
- 用户只要求人群倾向时，不修改 ROI、预算、素材、投放形象、开关、投放状态或商品价格。

## 执行流程

### 1. 锁定统计口径

1. 读取用户指定的投放时间范围；截图或页面显示的日期优先于默认“今天”。例如用户说“8 月 6 日至 8 月 16 日”，不得改读成单日数据。
2. 刷新官方「小店投放/商品托管」列表，读取全部分页。
3. 校验页面显示总数、各页返回行数之和、唯一 `platformGoodsId` 数量三者一致。失败时停止写入，只记录刷新或分页失败原因。
4. 按累计曝光数降序取目标数量，通常为前 10 个；保留商品 ID、标题、投放状态、曝光、点击、加购、成交订单、成交金额、花费、当前人群倾向和统计时间。
5. 只把当前官方列表和当前详情作为状态证据；旧快照只能补充不随状态变化的商品标题等元数据。

### 2. 建立商品人群假设

逐商品阅读标题、主图、规格和商品定位，写出“商品属性 -> 潜在人群 -> 设置理由”。使用以下初始策略，但必须结合具体商品修正：

| 商品特征 | 初始性别假设 | 初始年龄假设 | 城市 | 说明 |
|---|---|---|---|---|
| 甜点、饼干、桃酥、巧克力、早餐糕点 | 女 | 24-30 岁 | 不限 | 用女性作为第一轮垂直测试，年龄只先测试一个窄区间 |
| 卤味、鸭货、虾条、脆笋、辣味零食 | 不限 | 24-30 岁 | 不限 | 避免把明显大众或男性也可能购买的零食误判为女性专属 |
| 清洁、湿巾、鞋护、一次性耗材、厨房耗材 | 不限或按使用场景选择 | 24-30 岁或家庭主力年龄段 | 不限 | 先按场景和购买任务判断，不因“女性用品”字样直接锁死性别 |
| 牙刷、牙膏、电动牙刷等口腔护理 | 不限或根据商品传播定位选择 | 24-30 岁 | 不限 | “男女性伴侣通用”只能作为商品卖点，不能直接证明受众比例 |

这些是受控测试假设，不是最终事实。城市通常最后处理，因为城市同时收窄会显著减少探索流量；没有城市级点击、加购或成交证据时保持城市不限。

### 3. 进入详情并修改

对每个目标商品执行以下低自由度步骤：

1. 通过当前列表中精确商品 ID 的“查看详情”进入详情页。
2. 校验详情页的 `platformGoodsId`、标题和投放状态与列表目标一致；不一致时返回列表，不按标题相似匹配。
3. 找到“人群倾向”区域，确认当前设置。优先点击该区域的编辑入口，不要把“投放形象”的“修改”当成人群倾向入口。
4. 只修改已分析的性别、年龄、城市字段；保留其他设置不变。
5. 保存后等待官方反馈，重新读取详情摘要中的性别、年龄和城市。
6. 只有保存成功且摘要逐字段等于目标设置，才记录“人群倾向修改完成”；否则记录失败原因，不声称完成。

### 4. 设计验证周期

每次修改必须记录修改前后数据和假设：

```text
platformGoodsId | 统计窗口 | 修改时间 | 修改前 | 修改后 | 属性依据 |
曝光 | 点击 | CTR | 加购 | 订单 | 成交金额 | 花费 | 回读结果
```

不要把零花费、零点击、零加购、零订单的数据解释为“人群已经验证”。这类数据只能说明尚未获得效果证据。

默认验证规则：

- 数据极少时，保持城市不限，只测试一个主要变量；不要同时大幅收窄性别、年龄和城市。
- 有足够点击但无加购或订单时，优先回扩最近修改的变量，并检查商品素材、价格和商品承接页；人群调整不能替代其他问题诊断。
- 点击率和加购率改善且出现成交时，保留当前人群，下一轮只调整一个变量。
- 出现明确的城市级点击、加购或成交集中后，才考虑城市收窄；城市收窄后必须保留回扩方案。
- 效果恶化或样本不足时回滚到上一个已回读配置，不回滚到未经验证的历史快照。

### 5. 结果归档

每个商品至少留存：

- 精确 `platformGoodsId`、商品标题、统计窗口和累计曝光排名。
- 修改前后的人群倾向、保存时间、官方详情回读结果。
- 商品属性分析和初始假设，明确标注“受控测试假设”或“数据验证结论”。
- 修改前后曝光、点击、加购、订单、成交金额、花费及可计算的 CTR/加购率/成交率。
- 未执行原因，例如“刷新失败”“详情 ID 不一致”“保存失败”“数据不足不收窄城市”。

## 完成判定

只有同时满足以下条件才可说某商品的人群倾向修改完成：

1. 当前官方列表刷新成功，统计窗口正确，全部分页校验通过。
2. 精确商品 ID 详情页显示目标商品和当前投放状态。
3. 人群倾向保存请求成功。
4. 同一次官方会话的详情摘要逐字段回读成功。
5. 记录了商品属性假设和修改前后数据。

“已保存”不等于“已验证有效”；“诊断结果优秀”也不能代替人群设置的逐字段回读。

## 常见错误

- 把单日窗口误当成用户要求的累计窗口。
- 只读第一页就声称完成前 10 排名。
- 按标题相似、行顺序或旧快照猜商品 ID。
- 同时收窄性别、年龄、城市，却没有实验对照。
- 因为商品是女性可能购买就直接设置女性，不写商品属性依据。
- 把零花费或零订单解释成“女性/24-30 岁已验证”。
- 误点“投放形象修改”导致视频号形象被修改。
- 为了追求转化率而顺手改预算、ROI、素材或投放开关。

## 本任务的可复用示例

对于累计曝光靠前的零食商品，可以先将甜点类设为“女、24-30 岁、城市不限”，将卤味或大众咸味零食设为“性别不限、24-30 岁、城市不限”。这只是基于商品属性的第一轮受控测试；后续必须根据同一统计口径下的点击、加购和成交数据决定继续收窄或回扩。
## Windows Repo Mirror Notes

This skill keeps the same official Weixin Shop browser workflow on Windows. It does not need a separate PowerShell or `.cmd` business launcher: use the shared Codex `chrome-devtools-mcp` workflow and the same live-session read, save, and official-detail reread rules.

When browser recovery needs keyboard input through `press_key`, use Windows-friendly equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back and forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\weixin-shop-audience-targeting\\`. Keep screenshots, structured experiment records, exported logs, and copied attachments quoted and in `C:/Users/<name>/...` form instead of `/Users/...`; use quoted UNC or mapped-drive paths when reading shared evidence, for example `\\\\BSJT168\\BSJT 共享给我\\AI专用\\[Codex]Mac部署\\旺店通`.

Use PowerShell path quoting when invoking any optional local inspection helper, and keep environment changes session-scoped. Do not create a `.cmd` wrapper, persist variables with `setx`, or store cookies, tokens, signed URLs, credentials, or raw request headers in Windows evidence files. The browser session must remain the source of truth for the official list, detail, save result, and field-by-field reread.
