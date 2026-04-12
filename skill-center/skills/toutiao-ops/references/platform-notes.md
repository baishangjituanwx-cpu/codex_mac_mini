# Toutiao Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 图文创作与修改

Sources:
- https://baike.toutiao.com/detail/211/212/214

Updated by platform:
- 2025-02-19

Key points:
- Official article publishing supports manual posting and `内容源同步`.
- PC entry: `头条号后台 -> 主页 -> 创作 -> 图文`.
- Mobile entries:
- `今日头条 APP -> 首页右上角发布按钮 -> 写文章`
- `今日头条 APP -> 我的 -> 创作中心 -> 发布 -> 写文章`
- Each article supports at most 5 edits.
- Articles older than 14 days, or articles limited by legal or community issues, cannot be edited in place.
- Frequent deletion, modification, or repeated publication can hurt recommendation.

### 登录与安全验证

Source:
- https://baike.toutiao.com/detail/204/259/0

Updated by platform:
- 2025-02-21

Key points:
- Desktop login supports SMS login, password login, and authorized 抖音 login.
- If the current device and browser have not passed SMS verification in the last 30 days, login or publish-time verification may be triggered.

### 图文收益

Source:
- https://baike.toutiao.com/detail/192/198/0

Updated by platform:
- 2025-01-02

Key points:
- Article收益 requires joining `创作者计划`.
- The article can opt into `投放广告赚收益` from the publish settings.
- Revenue viewing paths are in the app creator center and desktop收益 data surfaces.

### 头条首发

Source:
- https://baike.toutiao.com/detail/242/566/0?enter_from=left_navigation

Updated by platform:
- 2026-03-16

Key points:
- `头条首发` is a per-article declaration.
- Eligibility requires original content, more than 100 Chinese characters, first publication on 头条, and no publication to other platforms within 72 hours after posting.
- The platform rewards quality across five dimensions:
- 时效
- 原创深度
- 信息增量
- 创作规范
- 用户价值
- Plagiarism, stitched content, public-information aggregation, and low-quality templated writing are explicit high-risk failure modes.

### 信用分机制

Source:
- https://baike.toutiao.com/detail/236/470/0?enter_from=left_navigation

Updated by platform:
- 2026-03-24

Key points:
- Credit starts at 100.
- Violations deduct points and can close the account when credit reaches 0.
- Official examples include rumors, vulgar inducement, misleading commercial claims, severe clickbait, image-text mismatch, and improper 首发 declaration.

## Operating Guidance

- For review work, map each post to the five official 首发 quality dimensions even when 首发 is not enabled.
- For promotional copy, audit exaggeration, unsupported guarantees, and weak evidence before focusing on hooks.
- For comment ops, treat spam and rumor-bait as moderation problems, not engagement opportunities.

## Local Practice Notes

- Current workspace lesson: missing desktop login state can leave the flow stuck on verification-code login, and password-login switching may not reveal the password form reliably.
- Current workspace lesson: the cover picker exposes two image file inputs, but the first image input is the reliable one for reaching `已上传 1 张图片`.
- Current workspace lesson: after `预览并发布`, the real final submit action is `确认发布`.
- Current workspace lesson: for longer article bodies, DOM paragraph injection was more stable than large keyboard text insertion.
- Always verify from `作品管理` or a public URL after publish.
- If the task expands into browser execution, also load `$social-publish-automation`.
