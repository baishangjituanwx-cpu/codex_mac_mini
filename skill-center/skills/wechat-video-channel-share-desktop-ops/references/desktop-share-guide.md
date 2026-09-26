# Desktop Share Guide

This guide is for operating WeChat Channels sharing from the macOS WeChat desktop client.

## Scope

Two actions are covered here:

- Forward a Channels post into one or more chats or groups
- Share a Channels post to Moments

## Before You Start

1. Confirm the installed Mac WeChat version:
   ```bash
   python3 /Users/z/.codex/skills/wechat-video-channel-share-desktop-ops/scripts/check_wechat_video_channel_share_support.py
   ```
2. Make sure the account can see the left-sidebar `视频号` entry.
3. Make sure the target group already exists and is visible in desktop WeChat.
4. If the goal is Moments sharing, prefer a build at or above the public `3.4.0.2` baseline.

## Live-Tested Notes On This Machine

These were directly observed on the current Mac WeChat build on `2026-04-04`:

- `窗口` menu exposes stable entries for `聊天`、`通讯录`、`收藏`、`朋友圈`.
- `Cmd+F` in the main chat window opens the left search box and shows a `搜索网络结果` suggestion row.
- The current build still shows the left sidebar icons for `聊天 / 通讯录 / 收藏 / 视频号 / 其他入口`, but external coordinate clicking on the `视频号` icon was not stable enough to treat as an automation-safe primary path.
- Opening `朋友圈` through `窗口 -> 朋友圈` is currently more reliable than trying to hit the card window through loose coordinates.
- A public Channels short link like `https://weixin.qq.com/sph/...` can be sent into `文件传输助手`; clicking that link inside desktop WeChat opens the Channels detail page.
- On this machine, the `转发给朋友` flow opened a desktop picker titled `微信发送给`, allowed selecting more than one group, and changed the green button to `分别发送(2)`.
- In that `微信发送给` picker, the top-left field is still the recipient search field. The forwarding note belongs in the bottom-right input box above the green send button.

Implication:

- For scripted or assisted operation, prefer menu entries when they exist.
- Treat the `视频号` sidebar icon as a live-verify item unless you have a current, confirmed hit target.

## A. Forward a Channels Post to a Group

Treat this as the stable desktop workflow:

1. Open Mac WeChat.
2. Enter `视频号` from the left sidebar, or use a verified public short link fallback if the sidebar entry is awkward to hit.
3. Open the target video post.
4. Find the post-level share entry.
   Common patterns on desktop are:
   - a share arrow
   - `...`
   - a context action near the post card
5. If the share sheet shows `转发给朋友` or `发送给朋友`, choose it.
6. In the `发送给` or `微信发送给` picker, use the top-left search field only to search chats or groups.
7. Select the target group or groups.
8. If you want to add copy, type it in the bottom-right note box above the green send button.
9. Confirm the send action.
10. Verify that a Channels card or link preview appears inside the target group chat.

Practical notes:

- On this machine, the picker did allow selecting two groups in one flow and the button changed to `分别发送(2)`.
- If the picker is visible but the addressee dialog drifts offscreen during automation, treat the right panel as the source of truth: selected recipients appear there, and the green button text reflects the recipient count.
- If the share sheet does not show a direct chat target, try a copy-link style path first, then paste the link into the group chat manually.
- If neither direct sharing nor link copying is exposed on the current Mac build, use mobile WeChat as the fallback.
- On this machine, if the `视频号` sidebar icon is difficult to hit through automation, a practical fallback is:
  1. copy the short link from `视频号助手`
  2. send that link into `文件传输助手`
  3. click the link to open the Channels detail page inside desktop WeChat
  4. continue from the post-level share menu

## B. Share a Channels Post to Moments

Treat this as the stable desktop workflow:

1. Open Mac WeChat.
2. Enter `视频号`.
3. Open the target video post.
4. Open the post share menu.
5. If `分享到朋友圈` is available, choose it.
6. Enter the Moments compose screen.
7. Add optional text.
8. Review any visibility settings the current build exposes.
9. Publish.

Practical notes:

- Desktop Moments support arrived earlier than Channels-to-Moments sharing. Do not assume that every build with Moments support can also share Channels content to Moments.
- If the current desktop build can post Moments but the Channels share sheet has no `分享到朋友圈`, treat that as a build/UI/account limitation and fall back to mobile WeChat.
- On this machine, `窗口 -> 朋友圈` is a verified stable entry to open the desktop Moments window. The top-right publish controls inside the Moments window still need live verification before scripting because the visible camera icon did not yet prove to be a reliable external click target.

## C. What To Say When the UI Differs

Use this wording pattern:

- `Mac 微信上这个能力大概率是支持的，但当前版本的按钮位置可能有漂移，我先按“视频号 -> 打开作品 -> 分享/更多 -> 发送给朋友或分享到朋友圈”这条路径核。`

This keeps the answer accurate without overclaiming exact placement.

## D. Troubleshooting

### No `视频号` entry in the sidebar

- Likely too old a version, or the current account/build has not exposed the entry.
- Compare against the `3.3.0` baseline first.

### Can open Channels, but no `分享到朋友圈`

- Compare against the `3.4.0.2` baseline first.
- If the installed build is clearly newer, treat it as UI drift or account-specific rollout and use phone fallback if needed.

### Can share to a chat, but group target is awkward to find

- Use the desktop search inside the target picker if available.
- Do not type the forwarding copy into that top-left search field; that field only filters recipients.
- Put any forwarding note into the bottom-right note box above the green send button.
- If the share target picker is weak, copy the link and paste it into the group manually.

### The user wants automation

- First live-verify the current share sheet on the target Mac build.
- After that, pair this skill with `/Users/z/.codex/skills/wechat-desktop-ops/SKILL.md` and `/Users/z/.codex/skills/wechat-moments-desktop-ops/SKILL.md`.
