# Official Notes

This file records the stable external guidance that matters for Mac WeChat desktop automation.

## WeChat on Mac

Source:

- App Store listing: <https://apps.apple.com/us/app/wechat/id836500024?mt=12>

Useful points from the App Store page:

- The Mac app is published as `WeChat` by `Tencent Mobile International Limited`.
- The listing is marked `Only for Mac`.
- The Mac listing states WeChat is available for desktop use.
- The current App Store page says it requires `macOS 12.0 or later`.

Why it matters:

- This confirms the Mac client is an official distribution channel.
- It gives the baseline OS support expectation for automation hosts.

## macOS Permissions Required by Desktop Automation

### Accessibility

Source:

- Apple Support: <https://support.apple.com/guide/mac-help/-mh43185/mac>

Key point:

- Apps that access and control the Mac through accessibility features must be explicitly allowed in `System Settings > Privacy & Security > Accessibility`.

Why it matters:

- UI clicking, focus changes, and frontmost control can fail silently without this permission.

### Automation

Sources:

- Apple Support: <https://support.apple.com/guide/mac-help/allow-apps-to-control-other-apps-on-mac-mchl07817563/mac>
- Apple Support: <https://support.apple.com/en-lamr/guide/mac-help/mchl108e1718/mac>

Key point:

- macOS lets you turn app-to-app control on or off in `System Settings > Privacy & Security > Automation`.

Why it matters:

- AppleScript and System Events control of WeChat depend on this.

### Input Monitoring

Source:

- Apple Support: <https://support.apple.com/en-afri/guide/mac-help/mchl4cedafb6/mac>

Key point:

- macOS controls whether apps can monitor keyboard, mouse, or trackpad input in `Privacy & Security > Input Monitoring`.

Why it matters:

- Keyboard-driven send actions and some simulated input flows can break without this grant.

### Screen and System Audio Recording

Source:

- Apple Support: <https://support.apple.com/en-afri/guide/mac-help/mchl592e5686/mac>

Key point:

- macOS requires explicit permission for apps that use screen capture in `Privacy & Security > Screen & System Audio Recording`.

Why it matters:

- OCR-based chat reading depends on desktop screenshots.

### Notifications

Source:

- Apple Support: <https://support.apple.com/guide/mac-help/notifications-settings-mh40583/mac>

Key point:

- macOS notification settings control alert style, previews, and app icon badges.

Why it matters:

- Hidden-idle wake logic is more reliable when WeChat still exposes unread state through the menu bar or Dock badge.

## Usage Guidance

- Prefer the official Mac App Store build for a cleaner baseline.
- If automation stops working after a macOS update, re-check all four privacy permission categories before changing code.
- If unread wake logic looks dead while the app is hidden, inspect WeChat notification settings plus macOS notification and badge behavior.
