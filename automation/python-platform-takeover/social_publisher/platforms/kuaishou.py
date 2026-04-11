from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class KuaishouPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="kuaishou",
        display_name="快手",
        compose_urls=["https://cp.kuaishou.com/article/publish/video?tabType=1"],
        management_urls=["https://cp.kuaishou.com/article/manage/video"],
        prechecks=[
            "先看作品管理有无重复",
            "遇到继续编辑提示优先续作",
            "重读 #work-description-edit 的真实内容",
        ],
        manual_checkpoints=[
            "登录态恢复",
            "上传封面后人工确认",
        ],
        success_signals=[
            "作品管理出现新条目",
            "状态为审核中",
        ],
        takeover_allowed=[
            "顶部提示继续编辑的草稿页",
            "视频已上传但还没最终提交的页",
        ],
        takeover_stop_conditions=[
            "作品管理已有同 description 和同视频",
            "当前草稿内容和本次发布包不一致",
        ],
    )
