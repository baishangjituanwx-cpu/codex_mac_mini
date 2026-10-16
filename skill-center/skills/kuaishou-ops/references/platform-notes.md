# Kuaishou Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 快手官网与创作者服务入口

Sources:
- https://kuaishou.cn/about/index.html
- https://cp.kuaishou.com/article/publish/video?tabType=1

Observed on:
- 2026-04-02

Key points:
- The official 快手 about page links directly to:
- `创作者服务平台`
- `上传视频`
- `帮助中心`
- `社区规范`
- The official web publish page exists under `cp.kuaishou.com/article/publish/video?tabType=1`.

### 举报与社区治理

Source:
- https://www.kuaishou.com/help/report

Observed on:
- 2026-04-02

Key points:
- The official report page says 快手 aims to maintain a healthy and positive content platform.
- It documents report handling for harmful live content and references `快手社区管理规范`.
- This is a useful official pointer for moderation and interaction boundary decisions.

## Operating Guidance

- For review work, separate creator-side list status from public distribution strength.
- For comments, respond to useful questions early and treat harmful or spammy replies as moderation work.
- For content optimization, focus on a clearer opening, easier comprehension, and stronger scene fit before changing everything else.

## Local Practice Notes

- Current workspace lessons:
- the draft-resume path is workable when the first upload lands in an editable draft
- final verification should happen in `作品管理`
- `审核中` is the expected state after submit
- for larger local videos, page-side CDP `DOM.setFileInputFiles` was more reliable than ordinary remote `setInputFiles`
- the verified description editor node was `#work-description-edit`
- the effective publish control was the bottom action area containing `发布 / 取消`
- In the verified 2026-04-04 retry flow, the preferred cover path changed:
- first click the top warning-bar `继续编辑` to resume the unfinished draft
- then switch to `上传新封面 / 上传封面 / 更换封面`
- write the prepared local cover into the image file input
- recheck the preview really changed before clicking publish
- founder-IP default changed on 2026-04-05: do not use `智能推荐封面` unless the user explicitly asks for it again
- If the task expands into browser execution, also load `$social-publish-automation`.
