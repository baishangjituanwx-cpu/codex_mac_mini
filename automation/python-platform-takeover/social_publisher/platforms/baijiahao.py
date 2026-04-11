from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class BaijiahaoPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="baijiahao",
        display_name="百家号",
        compose_urls=["https://baijiahao.baidu.com"],
        management_urls=["https://baijiahao.baidu.com/builder/rc/home"],
        prechecks=[
            "先查作品管理确认同标题未重复",
            "正文和封面都对齐本次发布包",
        ],
        manual_checkpoints=[
            "百度安全验证",
            "登录态恢复",
        ],
        success_signals=[
            "提交成功，正在审核中",
            "内容管理出现新条目",
        ],
        takeover_allowed=[
            "标题和正文已填好，只差最终提交的图文页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同标题或同正文片段",
            "当前页面残留无法确认来源的旧草稿",
        ],
    )
