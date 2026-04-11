# GitHub 上传前检查表

## 必删或必忽略

- `.bridge.env`
- `.codex-feishu-bridge/`
- `bridge.log`
- `bridge.stdout.log`
- `bridge.stderr.log`
- 任意验证码截图
- 任意 chat id、app id、app secret
- 本机绝对路径里带用户隐私的信息

## 建议不传

- 大体积原始视频
- 中间导出素材
- 浏览器临时截图
- 风控页面截图

## 建议保留

- skill 包
- SOP 文档
- 模板
- 最近成功案例的 Markdown 包
- 发布日志
- 初始化脚本

## 上传前最后确认

1. `README.md` 能解释清楚整套流程
2. 飞书桥接目录能独立部署
3. 模板目录足够新 campaign 直接复用
4. 示例里的绝对路径都已经替换成占位符
5. 没有把真实飞书配置提交进去

