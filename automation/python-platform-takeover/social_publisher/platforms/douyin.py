from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class DouyinPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="douyin",
        display_name="抖音",
        compose_urls=["https://creator.douyin.com"],
        management_urls=["https://creator.douyin.com/creator-micro/content/manage"],
        prechecks=[
            "先看作品管理顶部最近两条",
            "标题必须走真实输入",
            "封面优先准备 3:4 和 4:3 两版",
        ],
        manual_checkpoints=[
            "登录和风控验证",
            "封面裁切后人工确认",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中或已发布",
        ],
        takeover_allowed=[
            "视频已上传且标题、描述与本次发布包一致的草稿页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同视频",
            "标题或描述仍然是上一次选题",
        ],
    )
