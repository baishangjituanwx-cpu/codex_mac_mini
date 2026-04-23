# Xiaohongshu Platform Notes

Read only the sections needed for the current task.

## Official Sources

### 小红书官方 App 公开定位

Source:
- https://apps.apple.com/us/app/%E5%B0%8F%E7%BA%A2%E4%B9%A6-%E4%BD%A0%E7%9A%84%E7%94%9F%E6%B4%BB%E5%85%B4%E8%B6%A3%E7%A4%BE%E5%8C%BA/id741292507?l=zh-Hans-CN

Observed on:
- 2026-04-02

Key points:
- The official app listing positions 小红书 as a large lifestyle-interest community built around discovery and interaction.
- It explicitly frames the product around discovering content and meeting like-minded users, which is useful for judging note tone and community fit.

### 小红书大学入口

Source:
- https://school.xiaohongshu.com/en/open/index.html

Observed on:
- 2026-04-02

Key points:
- The official school homepage exposes `规则中心`, `帮助中心`, and `服务中心`.
- This is the best public official starting point for current platform-side rules and support routing.

## Operating Guidance

- Because public official creator-rule pages are not richly indexed, treat the official school entry as the canonical lookup surface and combine it with current platform responses.
- For ops work, separate three states:
- UI is reachable
- publish request is accepted
- note is actually visible in manager or public URL
- For packaging, prioritize cover-note relevance, concrete value, and native discussion tone over hard promotional wording.

## Local Practice Notes

- Current workspace lessons:
- creator publish may redirect to login if the creator session is missing
- a publish request can still be rejected with `-9136` for community-rule issues
- the real note-creation request hits `edith.xiaohongshu.com/web_api/sns/v2/note`
- `笔记管理` can lag after submit
- use the real publish button node, not wrapper text or container divs
- in remote CDP-attached Playwright, videos above 50 MB can fail through normal `setInputFiles`
- the stable workaround was to target the page-side file input with CDP `DOM.setFileInputFiles` and a local filesystem path
- the best verified success pattern was:
- submit response `success: true`
- captured `share_link`
- `笔记管理` shows the new note in `审核中`
- the verified manager path for duplicate checks is `https://creator.xiaohongshu.com/new/note-manager?source=official`
- the 2026-04-23 duplicate-publish failure happened because manager visibility lagged while there was no hard local receipt ledger to stop retries
- the hard-stop rule now is:
- check local receipt `automation/python-platform-takeover/state/publish-receipts/<campaign_id>.json`
- then check `笔记管理`
- if either side shows a blocking state such as `submitted / published / under_review / success / verified`, do not republish
- only clear the receipt after the old note is deleted, made private, or explicitly abandoned
- in the verified custom-cover path on 2026-04-03, `修改封面` lived behind the cover hover operator rather than a stable visible text button
- the real modal success signal was `上传图片`; waiting on the page section title `设置封面` was a false positive
- after custom cover upload and confirm, `笔记管理` showed the new short video `AI智能体把事做完 / 2026年04月03日 17:14 / 审核中`
- If the task expands into browser execution, also load `$social-publish-automation`.
