from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class ZhihuPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="zhihu",
        display_name="知乎",
        compose_urls=["https://zhuanlan.zhihu.com/write"],
        management_urls=["https://www.zhihu.com/creator/content"],
        prechecks=[
            "先看创作中心有无重复内容",
            "富文本字段必须真实激活",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "编辑器异常时人工重试",
        ],
        success_signals=[
            "公开文章页可见",
            "创作中心出现新文章",
        ],
        takeover_allowed=[
            "富文本已写入，当前页只差发布确认",
        ],
        takeover_stop_conditions=[
            "按钮灰着且编辑器未真正激活",
            "创作中心已有同标题",
        ],
    )
