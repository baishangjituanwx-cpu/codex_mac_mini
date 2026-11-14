# Douyin Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 抖音创作服务平台发布入口

Source:
- https://partner.open-douyin.com/docs/resource/zh-CN/mini-app/open-capacity/flow-entrance/douyin/video/common-mount

Observed on:
- 2026-04-02

Key points:
- The official doc states users can publish from the 抖音 App short-video page.
- It also documents the PC flow: login to `抖音创作服务平台`, click `发布视频`, upload the video, and then publish.
- The same document points to `抖音创作者中心` in-app as the place to view effective-fan, real-name, and violation information for capability eligibility.

### 中视频伙伴计划与统一分发

Source:
- https://creator.douyin.com/ixigua/mvp?enter_from=after_post_popup

Observed on:
- 2026-04-02

Key points:
- The official page says one publishing flow can distribute to 西瓜视频、抖音、今日头条 and manage content in one place.
- The page also says收益 is affected by watch time, content quality, and audience factors.
- It positions originality and copyright托管 as growth and收益 levers.

## Operating Guidance

- When the task involves tags,挂载, or special capabilities, check account eligibility first.
- For review work, separate three causes of underperformance:
- weak packaging
- weak vertical consistency
- account or capability restrictions
- For comment ops, prioritize clear user questions and conversion-intent comments over noisy debate.

## Local Practice Notes

- Current workspace lessons:
- upload and submit were straightforward after login
- post-submit verification should happen from creator-side management, not only from the composer
- `审核中` is the expected success-adjacent state after submit
- In the verified 2026-04-04 retry flow, `作品描述` filled successfully did not mean the publish form was complete.
- The separate title input `填写作品标题，为作品获得更多流量` stayed empty and blocked real submission even while the red `发布` button remained visible.
- In the verified 2026-04-05 follow-up, that title input still rejected direct DOM value writes. A real click plus keyboard typing was the stable fill path.
- In this flow, Douyin AI covers needed a two-step confirm:
- first set and confirm `横封面4:3`
- then switch to `设置竖封面`
- choose the vertical AI cover
- return to horizontal and click `完成`
- Default founder-video rule in this workspace changed on 2026-04-05: do not use Douyin `AI封面` by default.
- Use `上传封面` with prepared local assets for both `竖封面3:4` and `横封面4:3`.
- The theme text should sit in the middle area if needed so the manage-card thumbnail still shows the topic after crop.
- In the verified 2026-04-05 retry, a successful custom-cover upload required clicking the black `上传封面` tile and writing the local file into the tile-owned input, not only opening the modal.
- The stable verification pattern is: the central modal preview changes to the prepared cover, then the outer form shows `竖封面3:4 / 横封面4:3` instead of `选择封面`.
- Final verification should include the top row in `作品管理`, not only the editor state, because the compose page can stay open after a successful submit.
- If the task expands into browser execution, also load `$social-publish-automation`.
