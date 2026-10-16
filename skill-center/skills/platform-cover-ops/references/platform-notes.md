# Platform Cover Notes

Read only the section for the current platform.

## Cross-Platform Cover System

### Shared operating rule

- Solve cover problems in this order:
- identify the platform's true preview surface
- decide whether to use a frame pick or a custom uploaded image
- tighten the cover message to one conflict or one promise
- verify the result at small-card size
- do not force the same cover method onto every platform

### Shared packaging rule

- Keep one main subject, one main message, and one high-contrast focal area.
- Prefer short cover text rather than repeating the full title.
- When the platform crop is uncertain, keep the key text and face or product within the center-safe area.
- If the platform UI is weak or inconsistent, prepend a clean poster frame to the start of the video as a fallback.
- For founder-IP talking-head videos, face clarity, hairline, and upper-body framing matter more than fancy poster graphics.
- If the preview loses the founder's head or turns into a background shot, treat it as a failed cover even if the text looks good.

### Source-video rule

- When the source comes from 小云雀 or another upstream video generator, finish source QA before touching platform cover tools.
- Minimum QA for this workspace:
- the identity still reads as the intended founder
- the scene matches the spoken message
- the subtitles stay short enough for mobile scanning
- one vertical master asset exists before platform-specific cover edits begin
- In the verified 2026-04-04 founder flow, subtitle lines capped to about 8 Chinese characters were easier to reuse across 抖音、视频号、快手 without crowding the cover area.
- From 2026-04-06 onward, the default post-generation cover rule is:
- after 小云雀 outputs the video, immediately make one `3:4` vertical cover and one `4:3` horizontal cover
- add one 8 to 10 Chinese-character theme to both covers
- treat those prepared covers as the publish-ready source for 抖音、快手、B站、视频号、微博
- and treat the same local cover package as the default article-cover source for 百家号、今日头条 / 头条号、知乎
- do not leave any of those five platforms on default frame cover or AI cover unless the user explicitly overrides that rule

## 微博

### Official source

Source:
- https://kefu.weibo.com/faqdetail?id=21317

Observed on:
- 2026-04-03

Key points:
- 微博官方视频上传规范支持常见比例 `16:9`、`1:1`、`9:16`。
- The same rule page is primarily about upload compatibility, which means the platform does expect video-surface cover presentation rather than only plain text posts.

### Cover mechanics

- In common 微博图文 workflows, the first image behaves like the real cover.
- In 微博视频 workflows, the video cover still matters, but it competes with the opening line much more than on pure video platforms.

### Practical cover strategy

- Use one strong first image instead of a dense poster wall.
- Keep cover text minimal or skip text entirely if the first sentence already carries the hook.
- For video, make the cover and the first 18 to 24 Chinese characters tell the same story.
- For 小云雀 founder videos in this workspace, prepare the final poster before opening 微博发布页. If the current 微博 flow does not expose a separate cover upload, use the prepared poster as the first visible image or first stable poster frame instead of a raw default frame.

## 百家号

### Official sources

Sources:
- https://smartprogram.baidu.com/opensourcedocs/introduction/auditing_baijiahao/
- https://apps.apple.com/sg/app/%E7%99%BE%E5%AE%B6%E5%8F%B7/id1269408827

Observed on:
- 2026-04-03

Key points:
- The official 素材审核规范 explicitly rejects unclear, vulgar, obvious P图, text-heavy, table-like, or meme-style low-quality images.
- The same audit guidance flags image-text mismatch as a real quality problem.
- The official app description confirms 百家号 covers multiple content types and distributes into 百度 App, 好看视频, and 百度搜索.

### Cover mechanics

- 百家号图文 cover is a real distribution and审核 variable.
- AI-generated cover previews can fail in the current workspace and leave the confirm action disabled.

### Practical cover strategy

- Mirror the search-style question in the cover with a shorter problem cue.
- Use one scene, one screenshot, or one proof element rather than a brand poster.
- If AI cover generation is unstable, switch to manual local upload immediately.
- In the verified local path, the confirm button could appear as `确定 (1)`, not only exact `确定`.
- For 小云雀 founder-topic article packages in this workspace, use the prepared local cover as the default upload source instead of 百家号 AI 封图.

## 知乎

### Official sources

Sources:
- https://www.zhihu.com/knowledge-plan/manual
- https://www.zhihu.com/org_use_norm

Observed on:
- 2026-04-03

Key points:
- 官方创作手册强调 clear structure, trusted sources, and image use as supporting material.
- 官方机构规范明确不鼓励 unrelated or decorative images, hard ads, and misleading packaging.

### Cover mechanics

- 知乎对题图 or首图的容忍度，比对硬广封面的容忍度更高。
- In many article workflows, the opening image matters more than a loud marketing-style standalone cover.

### Practical cover strategy

- Use the cover or首图 as evidence, not hype.
- Prefer screenshots, diagrams, product flows, or concrete scene visuals.
- If the article relies on an abstract concept, make the image carry the missing real-world context.
- For 小云雀 founder-topic article packages in this workspace, use the prepared local cover as the default 题图 / 首图 asset whenever the article benefits from a clear opening visual.

## 今日头条 / 头条号

### Official sources

Sources:
- https://baike.toutiao.com/detail/211/212/214
- https://baike.toutiao.com/detail/236/470/0?enter_from=left_navigation

Updated by platform:
- 2025-02-19
- 2026-03-24

Key points:
- Official article publishing uses the creator backend and supports repeated article maintenance only within limits.
- The published credit rules explicitly list `图文不符` and severe clickbait as risk items.

### Cover mechanics

- 头条号 article packaging is highly sensitive to click-through.
- When an article gets impressions but no reads, cover and title are the first repair target.

### Practical cover strategy

- Replace abstract brand or concept posters with a concrete business problem.
- Use a manual custom cover whenever the automatic result looks generic.
- Keep the cover and title tightly aligned to avoid both low CTR and image-text mismatch risk.
- For 小云雀 founder-topic article packages in this workspace, use the prepared local cover as the default upload source instead of a generic automatic cover.

## 抖音

### Official sources

Sources:
- https://partner.open-douyin.com/docs/resource/zh-CN/mini-app/open-capacity/flow-entrance/douyin/video/common-mount
- https://partner.open-douyin.com/docs/resource/zh-CN/mini-app/develop/server/content/video/create

Observed on:
- 2026-04-03

Key points:
- The official docs confirm both app-side and PC-side video publishing exist.
- The official server-side video create doc exposes dedicated cover-related parameters such as custom cover image and cover time, which means the platform treats cover selection as a first-class publish input rather than a cosmetic afterthought.

### Cover mechanics

- In current practical workflows, Douyin often provides a default or AI-assisted cover result after upload.
- That default should be treated as a draft.

### Practical cover strategy

- Always do a manual second edit after upload.
- Choose the frame before subtitles, chapter labels, or motion blur damage readability.
- Keep the cover promise identical to the first 1 to 3 seconds of the video.
- If text is used, make it very short and large. Small poster text dies in Douyin feed thumbnails.
- For 小云雀 founder videos in this workspace, use the prepared `3:4` and `4:3` uploaded covers as the default path before considering any AI-generated cover.
- If the user prefers Douyin's own AI cover, choose the platform AI path first.
- In that path, do not stop after horizontal cover selection. The verified local sequence was:
- choose `横封面4:3`
- switch to `设置竖封面`
- keep iterating vertical AI candidates until the person is clearly visible
- return and click `完成`
- For founder-IP covers, reject AI candidates that show mostly office background or crop away the body.

## 小红书

### Official sources

Sources:
- https://school.xiaohongshu.com/en/open/index.html
- https://apps.apple.com/us/app/%E5%B0%8F%E7%BA%A2%E4%B9%A6-%E4%BD%A0%E7%9A%84%E7%94%9F%E6%B4%BB%E5%85%B4%E8%B6%A3%E7%A4%BE%E5%8C%BA/id741292507?l=zh-Hans-CN

Observed on:
- 2026-04-03

Key points:
- The official school homepage is the current public rule and support entry.
- The official app description frames 小红书 as a discovery-driven lifestyle-interest community.

### Cover mechanics

- 小红书 cover is the note card.
- If the cover looks like a generic brand ad, it usually underperforms even when the content itself is fine.

### Practical cover strategy

- Design the cover like a native note, not a platform brochure.
- One person, one object, one scenario, one line of value.
- For video notes, if the editor does not give enough cover control, prepend a clean poster frame to the first half second of the video.
- Relevance between cover and正文 is more important than visual polish alone.

## 微信视频号

### Official sources

Sources:
- https://training.tencentads.com/uploads/202108/qScnaaFK_t6LQKJ.pdf
- https://channels.weixin.qq.com/platform/post/create
- https://channels.weixin.qq.com/micro/content/post/list

Observed on:
- 2026-04-03

Key points:
- The official Tencent training PDF confirms 视频号助手 is the desktop publish surface.
- The current live UI in this workspace exposes `编辑封面`, `从视频中选择封面`, and `上传封面`.
- The same current UI shows a `个人主页和分享卡片(3:4)` preview mode, which means cover crop must be checked beyond the raw editor canvas.

### Cover mechanics

- For 小云雀 founder videos in this workspace, 视频号 should default to `编辑封面 -> 上传封面`, using the prepared local vertical cover rather than the default video frame.

- 视频号 default first frame is often too weak.
- The verified local cover editor path was:
- entry `.edit-btn.edit-btn-zIndex`
- frame picker `.key-frames-slider`
- confirm `确定`

### Practical cover strategy

- Always open the cover editor after upload.
- If the first clear frame is weak, upload a prebuilt custom cover.
- Check both homepage preview and share-card preview before publishing.
- Keep the main subject central and avoid edge text because 3:4 share-card preview is unforgiving.
- In this workspace, `视频描述` and `短标题` must be filled together with the cover. Treat them as part of the publish-ready state, not optional metadata.
- If custom cover upload is unstable, a strong fallback is to reopen `编辑` and pick a frontal keyframe where the founder's face is fully visible in the 3:4 preview.

## 快手

### Official sources

Sources:
- https://www.kuaishou.com/help/feedback/4000
- https://cp.kuaishou.com/article/publish/video?tabType=1

Observed on:
- 2026-04-03

Key points:
- 快手官方帮助中心明确写明: desktop upload supports editing description, `自定义封面`, and publish time after upload.
- The official desktop publish route is under `cp.kuaishou.com`.

### Cover mechanics

- 快手 supports custom cover in official desktop upload flows, but exact controls can vary by route.
- In weak routes, key-frame selection may be the practical fallback.

### Practical cover strategy

- Prefer a direct action frame or uploaded custom cover over a random default frame.
- Use grounded, native-looking visuals rather than overdesigned posters.
- If the current route does not expose a stable custom-cover control, prepend a strong poster frame to the video head as insurance.
- Founder-IP default changed on 2026-04-05: use `上传新封面 / 上传封面 / 更换封面` with prepared local cover art, not `智能推荐封面`.
- For short-video creator-center cards, center-placed theme text can be safer than lower-third text because management thumbnails often crop away the bottom area.
