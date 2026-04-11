from social_publisher.platforms.baijiahao import BaijiahaoPublisher
from social_publisher.platforms.douyin import DouyinPublisher
from social_publisher.platforms.kuaishou import KuaishouPublisher
from social_publisher.platforms.toutiao import ToutiaoPublisher
from social_publisher.platforms.wechat_channels import WeChatChannelsPublisher
from social_publisher.platforms.weibo import WeiboPublisher
from social_publisher.platforms.xiaohongshu import XiaohongshuPublisher
from social_publisher.platforms.zhihu import ZhihuPublisher


REGISTRY = {
    "baijiahao": BaijiahaoPublisher,
    "douyin": DouyinPublisher,
    "kuaishou": KuaishouPublisher,
    "toutiao": ToutiaoPublisher,
    "wechat_channels": WeChatChannelsPublisher,
    "weibo": WeiboPublisher,
    "xiaohongshu": XiaohongshuPublisher,
    "zhihu": ZhihuPublisher,
}


def build_publisher(platform_id: str):
    try:
        publisher_cls = REGISTRY[platform_id]
    except KeyError as exc:
        raise KeyError(f"Unsupported platform: {platform_id}") from exc
    return publisher_cls()
