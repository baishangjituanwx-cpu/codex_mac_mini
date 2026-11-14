# Toutiao Publish Notes

Read only the sections needed for the current task.

## Official Workflow Sources

### 图文创作

Source:
- https://baike.toutiao.com/detail/211/212/214

Updated by platform:
- 2025-02-19

Key points:
- There are two official publishing paths for articles:
- manual posting on 头条号
- `内容源同步` from another platform
- PC manual entry: `头条号后台 -> 主页 -> 创作 -> 图文`
- Mobile manual entry:
- `今日头条 APP -> 首页右上角发布按钮 -> 写文章`
- `今日头条 APP -> 我的 -> 创作中心 -> 发布 -> 写文章`
- Edit path:
- PC: `管理 -> 作品管理 -> 文章 -> 修改`
- Mobile: `我的 -> 创作中心 -> 找到文章 -> ... -> 修改`
- Each article supports at most 5 edits.
- Articles older than 14 days, or articles limited by community or legal issues, cannot be edited in place.
- Delete or withdraw from the article-management page.
- The platform says daily publication is still capped at 50 items total even though earlier over-limit recommendation throttles were removed.
- Frequent deletion, modification, or repeated publication can affect recommendation.
- If the current device and browser have not passed phone verification in the last 30 days, publish-time phone verification may be required.

### 账号登录

Source:
- https://baike.toutiao.com/detail/204/259/0

Updated by platform:
- 2025-02-21

Key points:
- Desktop login supports:
- SMS login
- password login with phone or email
- authorized 抖音 login
- previously-authorized third-party login methods
- Mobile login supports 抖音 login, SMS login, password login, and identity-auth login.
- Official safety rule: if the account has not logged in on the current device and browser with SMS verification within 30 days, login or publish verification may fire.
- For account recovery and rebinding, the official path runs through the app-side help center.

### 文章创作收益

Source:
- https://baike.toutiao.com/detail/192/198/0

Updated by platform:
- 2025-01-02

Key points:
- To enable article revenue, the creator must join `创作者计划` in `今日头条 APP -> 我的 -> 创作中心 -> 查看创作者权限`.
- After rights are enabled, article posting can opt into `投放广告赚收益`.
- Mobile path: during posting, turn on the `头条广告` button.
- PC path: in the publish settings area, check `投放广告赚收益`.
- Existing published articles can enable ads later from article management, but articles that already enabled ads cannot switch ads back off.
- Revenue viewing paths:
- mobile: `我的 -> 创作中心 -> 收益提现`
- PC: `数据 -> 收益数据`

### 首发激励计划

Source:
- https://baike.toutiao.com/detail/242/566/0?enter_from=left_navigation

Updated by platform:
- 2026-03-16

Key points:
- `头条首发` is a per-article declaration on the publish page.
- Eligibility requires all of the following:
- article body over 100 Chinese characters
- original content
- first published on 头条
- not published on other platforms within 72 hours after posting on 头条
- account type is not 国家机构 or 新闻媒体, and 首发 permissions are available
- Current rule set:
- non-compliant content gets no basic or bonus first-publish payout
- non-first-publish content gets only base payout
- compliant first-publish content gets extra subsidy
- compliant and high-quality first-publish content can receive up to 5x extra subsidy
- Quality is judged on five dimensions:
- 时效
- 原创深度
- 信息增量
- 创作规范
- 用户价值
- High-risk first-publish failure modes:
- plagiarism, rewriting others, stitched compilations, and public-information aggregation
- marketing or traffic-driving copy submitted as "original"
- low-quality templated writing, messy formatting, machine-translation traces, or empty filler text
- republishing the same or substantially similar article after deletion
- Cross-posting within 72 hours after claiming first publish leads to credit deductions and loss of subsidy.

### 信用分机制

Source:
- https://baike.toutiao.com/detail/236/470/0?enter_from=left_navigation

Updated by platform:
- 2026-03-24

Key points:
- Credit starts at 100.
- Violations deduct 10 to 70 points.
- If credit reaches 0, the account is banned.
- Examples from the official deduction table:
- rumor or false information: 70
- vulgar inducement: 70
- illegal promotion: 20
- severe clickbait: 20
- false or misleading commercial claims: 20
- outdated content: 10
- image-text mismatch or weak relevance: 10
- low-quality formatting: 10
- improper `头条首发` declaration: 5
- The platform explicitly lists exaggerated claims such as `国家级`, `最XX`, `第一`, and guaranteed outcomes as risky examples in commercial content.

## Local Practice Notes

- Current workspace lesson from 2026-04-02:
- when desktop creator login state is missing, the 今日头条 flow may stay on the verification-code login page
- switching to password login may fail to reveal the password form reliably
- treat that as a manual login checkpoint before debugging anything inside the editor
- After a publish attempt, verify from `作品管理` or a public URL instead of trusting button state alone.
- If the task expands from 今日头条-only work to multi-platform publishing, also load `$social-publish-automation` for shared OpenCLI and Browser Bridge operating rules.
