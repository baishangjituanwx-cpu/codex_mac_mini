from social_publisher.platforms.base import PlatformMetadata, PlatformPublisher


class WeChatChannelsPublisher(PlatformPublisher):
    metadata = PlatformMetadata(
        platform_id="wechat_channels",
        display_name="微信视频号",
        compose_urls=[
            "https://channels.weixin.qq.com/login.html",
            "https://channels.weixin.qq.com/platform/post/create",
        ],
        management_urls=["https://channels.weixin.qq.com/micro/content/post/list"],
        prechecks=[
            "先确认 login.html 仍然有登录态",
            "真实表单在 iframe[name='content']",
            "先查列表页是否已有同视频",
        ],
        manual_checkpoints=[
            "登录失效",
            "上传卡住",
            "封面弹层需要人工复核",
        ],
        success_signals=[
            "create 页出现已发表",
            "列表页出现新条目且描述片段正确",
        ],
        takeover_allowed=[
            "视频已上传且短标题、描述已填的 ready 页",
            "删除错误成品后的同条修复页",
        ],
        takeover_stop_conditions=[
            "列表页已有同视频",
            "可见 UI 和 frame 真实状态不一致",
            "create 页跳回 login.html",
        ],
    )
