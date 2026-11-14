# Baijiahao Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 官方 App 能力说明

Source:
- https://apps.apple.com/sg/app/%E7%99%BE%E5%AE%B6%E5%8F%B7/id1269408827

Observed on:
- 2026-04-02

Key points:
- The official app description says 百家号 is a creator platform for `创作、发布、变现`.
- Supported content types include 图文、视频、动态、直播、图集.
- Official management capabilities listed in the app description include:
- `数据分析`
- `作品管理`
- `粉丝评论`
- `私信聊天`
- `收益分析`
- `账号注册、认证、信用分、权益申请`
- The same description says content can be distributed to 百度 App and 好看视频 and be indexed by 百度搜索.

### 百家号素材审核规范

Source:
- https://smartprogram.baidu.com/opensourcedocs/introduction/auditing_baijiahao/

Observed on:
- 2026-04-02

Key points:
- Title rules: no sensitive content, no title bait, no vulgarity, no wrong or garbled characters, no messy symbols.
- Image rules: avoid unclear, vulgar, gory, obvious P图, text-heavy, table, or meme-style low-quality images.
- Content rules: avoid vulgar, fake, bloody, or illegal content; timely articles are encouraged.
- Promotion rules: do not post QR codes, marketing phone numbers, watermarked promo images, malicious promotion, or third-party导流.
- Common failure patterns include title or image mismatch with landing content, forced促销 wording, and unclear or too-short titles.
- The policy also lists non-recommended or rejected categories such as rumors, misleading finance advice, old news posing as new, low-quality clickbait, and weak title-body relevance.

## Operating Guidance

- Because 百家号 distributes into 百度生态 and search, topic framing should answer a concrete user question instead of relying on vague branding language.
- In reviews, compare whether weak posts fail because of distribution, compliance, or weak packaging.
- Use comments and private messages as signals for next-topic planning, not only customer support.

## Local Practice Notes

- Current workspace lessons:
- final publish can be blocked by `百度安全验证`
- AI-generated cover previews may render as error or undefined and keep the confirm action disabled
- local manual cover upload resolved one blocked publish flow
- Real post-submit verification should use `https://baijiahao.baidu.com/builder/rc/content`, not only the home dashboard card.
- A valid success path can be: publish page shows `提交成功，正在审核中...`, then the new item appears in `作品管理` as `审核中`.
- Cover upload is stable when targeting the image input `input[type="file"][accept="image/*"]`.
- Duplicate same-title retries are dangerous on 百家号. In the verified local case, the second copy of the same article was judged `审核未通过 / 作品存在违规` while the earlier copy stayed `已发布`.
- Before any retry, open `作品管理` and search the exact title first. If the same-day item already exists in `已发布`, `审核中`, or `审核未通过`, stop and resolve the existing item instead of reposting.
- A delete action is not complete until the confirm dialog is accepted and the list refreshes without the duplicate row.
- Always verify final state from `作品管理`.
- If the task expands into browser execution, also load `$social-publish-automation`.
