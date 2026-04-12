# Official Notes

This file separates direct source evidence from inference for Mac WeChat Moments publishing.

## Direct Source Evidence

### Mac App Store listing

Source:

- https://apps.apple.com/cn/app/%E5%BE%AE%E4%BF%A1/id836500024?mt=12

What it directly confirms:

- The Mac app is `微信` by `Tencent Mobile International Limited`.
- The current Mac App Store listing says the app is for Mac and requires `macOS 12.0 or later`.
- The App Store release history currently lists:
  - `4.1.7` as the current visible version history entry
  - `4.1.4` with `朋友圈评论可发表情和图片`
  - `4.0.6` with `体验更新，Windows、Mac等多端统一` and `朋友圈可设置置顶内容`

Why it matters:

- This confirms the modern Mac client still has active Moments-related capability work.
- The `Windows、Mac等多端统一` note supports using current desktop UI parallels carefully.

## Public Reporting Used To Fill Historical Gaps

### 新浪科技, June 8, 2021

Source:

- https://finance.sina.com.cn/tech/2021-06-08/doc-ikqciyzi8448961.shtml

Reported points:

- Mac `3.1.0` beta supported `发表朋友圈` and `浏览朋友圈相册`.
- Before that, the Mac build had already gained browsing capability, and the new beta added publishing.

Use:

- Treat this as the historical signal that Mac desktop publishing started around `3.1.0` beta.

### IT之家, June 23, 2021

Source:

- https://www.ithome.com/0/558/839.htm

Reported points:

- Mac `3.1.1` official release supported `发朋友圈` and `浏览朋友圈相册`.
- The article describes the Mac publishing experience as close to the mobile flow.

Use:

- Treat `3.1.1` as the safer public baseline for official Mac desktop Moments posting.

## Inference Rules

These are reasonable, but still inferences:

1. The current Mac publish entry is likely aligned with modern Windows desktop entry placement because:
   - the App Store says Windows and Mac desktop experiences were unified in `4.0.6`
   - public desktop guides describe the Moments entry in the left sidebar and a compose control in the Moments page

2. A current Mac build newer than `4.1.4` should be assumed to support:
   - Moments posting
   - browsing the Moments album
   - pinning a Moments item
   - richer comment interactions such as emoji and image replies

3. Exact layout details may still drift by version, account flags, and gray releases, so live verification is preferred before scripting.
