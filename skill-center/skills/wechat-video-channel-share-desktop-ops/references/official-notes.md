# Official Notes

This file separates direct source evidence from historical public reporting and explicit inference for Mac WeChat desktop sharing of WeChat Channels content.

## Direct Source Evidence

### Mac App Store listing

Source:

- https://apps.apple.com/cn/app/%E5%BE%AE%E4%BF%A1/id836500024?mt=12

What it directly confirms:

- The Mac app is `微信` by `Tencent Mobile International Limited`.
- The current visible App Store version history shows `4.1.7`.
- The App Store release history also shows:
  - `4.1.4`: `朋友圈评论可发表情和图片`
  - `4.0.6`: `体验更新，Windows、Mac等多端统一` and `朋友圈可设置置顶内容`

Why it matters:

- This confirms that the modern Mac desktop client still has active Moments-related work.
- The `Windows、Mac等多端统一` note supports carefully using current desktop UI parallels when describing likely share paths.

## Public Reporting Used To Fill Historical Gaps

### 爱范儿 / AppSo, March 24, 2021

Source:

- https://www.ifanr.com/app/1407430

Reported points:

- Mac `3.0.0` beta could browse Moments.
- Mac `3.0.0` beta could browse Channels videos and Channels live streams that were shared in chats.

Use:

- Treat this as the early public signal that Mac desktop could already open chat-shared Channels content, even before a native Channels entry was added.

### 爱范儿 / AppSo, June 6, 2021

Source:

- https://www.ifanr.com/app/1421184

Reported points:

- Mac `3.1.0` beta added desktop Moments posting.
- The article also notes that sharing articles to Moments had not yet fully arrived at that stage.

Use:

- Treat this as the historical signal that Mac desktop Moments posting and desktop sharing enhancements arrived in phases, not all at once.

### IT之家, June 23, 2021

Source:

- https://www.ithome.com/0/558/839.htm

Reported points:

- Mac `3.1.1` official release supported posting Moments and browsing the Moments album.

Use:

- Treat `3.1.1` as the safer public baseline for official Mac desktop Moments posting.

### cnBeta, January 18, 2022

Source:

- https://www.cnbeta.com.tw/articles/tech/1227145.htm

Reported points:

- Mac `3.3.0` officially added a left-sidebar Channels entry.
- Users could click that entry to watch Channels content directly on Mac.

Use:

- Treat `3.3.0` as the public baseline for a native Channels entry in Mac WeChat.

### 界面新闻, March 25, 2022

Source:

- https://www.jiemian.com/article/7277253.html

Reported points:

- Mac `3.4.0.2` beta supported sharing public-account articles and Channels content to Moments.

Use:

- Treat `3.4.0.2` as the public baseline for Channels-to-Moments sharing on Mac desktop.

## Inference Rules

These are reasonable, but still inferences:

1. A current Mac build newer than `3.4.0.2` is likely new enough for desktop Channels-to-Moments sharing, but the exact share-sheet layout can still drift by version, account, or gray release.
2. A modern Mac build with a native Channels entry and normal chat-sharing controls will usually be able to forward a Channels post into group chats, but the exact `转发给朋友` or `发送给朋友` path should be live-verified in the current UI.
3. The desktop route for forwarding one Channels post to multiple groups should be treated as a repeat-per-group workflow unless the current build explicitly exposes a multi-target picker.
4. If a user asks for current exact button placement, answer with the best-known path and clearly label it as an inference unless you have direct local verification for that build.
