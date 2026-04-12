# Weibo Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 发布失败与自查

Source:
- https://kefu.weibo.com/faqdetail?id=13790

Updated by platform:
- 2025-05-19

Key points:
- Official failure causes include account restriction, community-rule violations, unsafe links, network or client issues, risky account state, and personal-attack content.
- If the failure is not explained by the visible error, the platform asks users to check the draft error prompt and file self-service feedback with screenshots.

### 创作者中心与数据中心

Source:
- https://kefu.weibo.com/faqdetail?id=21489

Updated by platform:
- 2026-03-09

Key points:
- `创作者中心` currently combines tasks, data reports, revenue center, rights center, hot activities, interaction tools, and related creator services.
- Entry points exist on both mobile and desktop, including `me.weibo.com`.
- Data caveats:
- `创作者中心` and `数据助手` may differ because of deduping and deleted-post handling.
- The center mainly exposes yesterday, 7-day, and 30-day windows rather than real-time intraday metrics.
- Public versus private traffic is separated.
- Accounts below 1 万粉 do not see full data-center detail.
- Reply likes under comments do not count toward yesterday's `转评赞`.

### 广告共享计划与收益影响因素

Source:
- https://kefu.weibo.com/faqdetail?id=20760

Updated by platform:
- 2025-12-22

Key points:
- Creator revenue can be checked from `创作者中心 -> 收益中心`.
- Official revenue drivers for 博文收益 include content quality, reading volume, and fan interaction quality.
- The platform explicitly says higher post frequency, higher activity participation, and stronger comment interaction can improve收益.
- The plan encourages original, real, valuable, positive content and penalizes falsehood, incitement, cyberbullying, and samey or low-quality content.
- Low credit or mute states can cancel or claw back收益.

### 协管员与互动管理

Source:
- https://kefu.weibo.com/faqdetail?id=21711

Updated by platform:
- 2024-09-30

Key points:
- `协管员` supports comment, 超话, and fan-group moderation.
- Entry is mobile-only.
- A creator can set up to 10 协管员.
- Creators can inspect operation logs, but they cannot undo a 协管员 action after it happens.

### 信用分与违规后果

Source:
- https://kefu.weibo.com/faqdetail?id=20822

Key points:
- Credit-history penalties cover comments, public posts, articles, videos, profile content, and private messages.
- The published table includes deductions for false information, personal attacks, cyberbullying, spam marketing, illegal content, vulgar content, bad value orientation, and违规活动.
- When credit-history points fall across threshold bands, behavior restrictions increase; at 0 the account is muted.

## Operating Guidance

- For postmortems, compare `公域/私域`, `转评赞`, follower change, and whether the post received creator-center recommendation exposure.
- For comment ops, answer high-intent comments early, then moderate hostility and spam.
- For monetized content, treat samey templated posts as a risk even if they are not formally rejected.

## Local Practice Notes

- Current workspace lesson: 微博发帖流程相对顺畅，主要工作重心在 public URL verification rather than UI clicks alone.
- If the task expands into browser execution, also load `$social-publish-automation`.
