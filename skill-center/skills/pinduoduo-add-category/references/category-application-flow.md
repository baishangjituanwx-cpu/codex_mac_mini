# Pinduoduo Category And Food-License Flow

## Browser Control

Use `mcp__chrome_devtools`:

1. `list_pages`
2. `select_page` or `navigate_page`
3. `take_snapshot`
4. `click` / `fill` / `press_key`
5. `evaluate_script` only for bounded DOM inspection or when normal clicks fail
6. `list_network_requests` and `get_network_request` when the page state disagrees with the UI

On Windows, this flow still uses the same MCP tools rather than a PowerShell wrapper. When you need a manual reload or location-bar recovery through `press_key`, use `Control+R` or `F5`, `Control+L`, `Control+A`, and `Alt+Left` / `Alt+Right`. If you save screenshots, evidence, or copied attachments locally during the workflow, keep those filesystem paths quoted and in `C:/...` form.

## Known Pages

- Entry: `https://mms.pinduoduo.com/goods/goods_list`
- Category qualification: `https://mms.pinduoduo.com/mallcenter/info/CategoryQualification`
- Operating license list: `https://mms.pinduoduo.com/mallcenter/info/licence`
- Prepackaged-food add form: `https://mms.pinduoduo.com/mallcenter/info/licence/1105/add`

Use the header search for `类目` if navigation is unclear. Search results may open duplicate tabs; use `list_pages` and select the newest relevant `mallcenter/info/...` tab.

## Route Selection

For requests like "申请新类目 休闲零食" or "用预包装食品备案凭证增加食品类目":

1. Check `店铺信息 > 类目资质` if the user specifically asks for category qualification.
2. If `休闲零食` is absent and the page only lists unrelated special categories, use `店铺经营许可证` instead of forcing the category page.
3. Click `添加证照`.
4. In `选择证照类型`, choose:
   - `食品经营许可`
   - `仅销售预包装食品备案凭证`
5. Confirm to open `/mallcenter/info/licence/1105/add`.

The user may call the document `预包装食品销售备案凭证`; Pinduoduo's UI label is normally `仅销售预包装食品备案凭证`.

## Form Mapping For 仅销售预包装食品备案凭证

Main fields observed on `/mallcenter/info/licence/1105/add`:

- `备案凭证`: required upload. Upload the user-provided certificate image or complete official public-record screenshot.
- `备案材料编号`: use the visible备案编号, usually beginning with `YB` or `BZ`. If the certificate has no备案编号, the page allows using the unified social credit code.
- `有效期截止至`: use a visible expiration date if present. A `备案日期` is not an expiration date. If no expiration date is present, choose `长期`.
- `经营范围`: check `仅销售预包装食品` unless the credential explicitly supports other listed ranges. Do not select `保健食品`, `婴幼儿配方乳粉`, or `特殊医学用途配方食品` unless the document explicitly says so.
- `是否含冷藏冷冻食品`: choose `是` if the credential says `含冷藏冷冻食品`; choose `否` if it says `不含冷藏冷冻食品`. If unclear, ask.
- `食品安全管理员`: use the visible legal representative, responsible person, operator, or user-provided administrator name only when appropriate. Ask if no suitable person is visible.
- `我方承诺`: check only when the form is otherwise ready and the user has authorized proceeding.
- `证照核实辅助材料` and official lookup URL are optional unless the page blocks submission or the user provides them.

Example from observed certificate:

- 备案编号: `YB14401150078431`
- 备案日期: `2025-09-19` (not an expiration date)
- 负责人: `陈永俊`
- 经营种类: `含冷藏冷冻食品，不含特殊食品`
- Resulting form choices: `长期`, `仅销售预包装食品`, cold/frozen `是`, administrator `陈永俊`.

## Upload And Submit

1. Use `upload_file` on the main `备案凭证` upload button.
2. Confirm upload success by checking that the upload button becomes disabled or a `预览` link appears.
3. Click `提交` only when the latest user message authorizes submission.
4. If the confirmation says roughly `预计在3个工作日内完成审核，请确认是否提交?`, click `确认` only if submission is authorized.
5. Immediately inspect the page after confirming. If a human-verification overlay appears, stop and ask the user to complete it. Do not report that there was no verification unless this check was actually done after final confirmation.

## Human Verification Handling

Stop and ask the user for manual handling when any of these appears:

- Slider puzzle text such as `请向右滑块完成拼图`
- CAPTCHA/image puzzle
- QR login
- SMS/OTP/password/account-security prompt
- A dimmed overlay that blocks the page after submit even if the a11y snapshot still shows the underlying list

After the user says they handled it, take a fresh snapshot and verify the final status. Mention that the user completed human verification if reporting the process.

## Verification Checklist

On `店铺信息 > 店铺经营许可证`, verify the application row:

- `经营许可类型`: usually `食品经营许可`
- `证照名称`: `仅销售预包装食品备案凭证`
- `截止日期`: entered date or `长期`
- `审核结果`: `审核中`, `审核通过`, or `驳回`
- `经营范围`: expected scope, such as `仅销售预包装食品`
- `提交时间`: current submission date

Report exact visible status and any platform estimate, such as `提交日起预计3个工作日内审核完毕`.
