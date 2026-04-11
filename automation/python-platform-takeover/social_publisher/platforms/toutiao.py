from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class ToutiaoPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="toutiao",
        display_name="今日头条 / 头条号",
        compose_urls=["https://mp.toutiao.com"],
        management_urls=["https://mp.toutiao.com/profile_v4/graphic/publish"],
        prechecks=[
            "入口走主页 -> 创作 -> 图文",
            "先看作品管理避免重复",
            "预览并发布后还要确认发布",
        ],
        manual_checkpoints=[
            "短信验证码",
            "登录态恢复",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中",
        ],
        takeover_allowed=[
            "标题、正文、封面都已就绪，只差二次确认的半成品页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同标题",
            "当前页卡在登录态且无法恢复",
        ],
    )
