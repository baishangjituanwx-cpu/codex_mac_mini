from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class WeiboPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="weibo",
        display_name="微博",
        compose_urls=["https://weibo.com"],
        management_urls=["https://weibo.com"],
        prechecks=[
            "发布前先查主页流，避免重复发相同主题",
            "主视频和正文保持第一屏一致",
        ],
        manual_checkpoints=[
            "登录态失效",
            "上传失败后手动重试",
        ],
        success_signals=[
            "主页流可见",
            "拿到帖子直链",
        ],
        takeover_allowed=[
            "视频已上传且正文与本次发布包一致的半成品页",
        ],
        takeover_stop_conditions=[
            "主页流已存在相同视频或正文片段",
            "当前字段明显是旧草稿",
        ],
    )
