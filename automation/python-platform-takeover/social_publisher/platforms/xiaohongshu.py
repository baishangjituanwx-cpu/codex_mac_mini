from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class XiaohongshuPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="xiaohongshu",
        display_name="小红书",
        compose_urls=["https://creator.xiaohongshu.com"],
        management_urls=["https://creator.xiaohongshu.com/publish/publish"],
        prechecks=[
            "先查笔记管理确认没有重复选题",
            "图文或视频模式要和本次内容包一致",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "风控和人工校验",
        ],
        success_signals=[
            "笔记管理出现新条目",
            "状态进入审核或已发布",
        ],
        takeover_allowed=[
            "内容和素材都已对齐，只差最终提交的草稿页",
        ],
        takeover_stop_conditions=[
            "笔记管理已存在同标题或同封面内容",
            "当前草稿无法确认属于本次任务",
        ],
    )
