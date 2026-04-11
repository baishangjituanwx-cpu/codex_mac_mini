# 仓库公开前检查表

这份检查表只做一件事:

在把当前仓库从 private 改成 public 之前，先把容易翻车的点过一遍。

## 先说结论

当前仓库可以公开，但建议先完成一轮“公开版清洗”。

重点不是代码能不能跑，而是这些内容一旦公开后，就会变成:

- 任何人都能直接查看
- 任何人都能 fork
- GitHub Actions 历史和日志也会变成公开可见

这一点可参考 GitHub 官方文档:

- [Setting repository visibility](https://docs.github.com/articles/making-a-private-repository-public)

## 公开前必须再扫一遍的内容

### 1. 密钥和鉴权信息

不要公开:

- 飞书 `App Secret`
- 任意 access token
- webhook 地址
- 本机 `.env`
- 登录态文件
- 浏览器 profile 目录

建议执行:

```bash
rg -n "token|secret|webhook|app_secret|APP_SECRET|authorization|Bearer " .
```

### 2. Chat ID 和内部群标识

如果你不希望外部看到内部通知目标，再扫一遍:

```bash
rg -n "oc_[A-Za-z0-9]+" .
```

### 3. 本机绝对路径

公开仓库前，尽量不要保留真实用户名和本机目录。

建议执行:

```bash
rg -n "/Users/|C:\\\\|Documents/New project|/Volumes/" .
```

### 4. 平台后台直链

平台后台 URL 可以保留，但如果其中混有:

- account id
- creator id
- query 里的敏感参数

就要改成无敏感参数的标准入口。

### 5. 示例内容的隐私

检查示例包里是否暴露了:

- 手机号
- 邮箱
- 客户名
- 未公开选题
- 内部运营节奏

## 公开前建议补的仓库元信息

这几项不是必须，但公开后会更完整:

- `LICENSE`
- 仓库 description
- repository topics
- `CONTRIBUTING.md`
- `CHANGELOG.md`

## GitHub 网页端改公开的路径

按 GitHub 官方文档，路径是:

1. 打开仓库主页
2. 点 `Settings`
3. 滚到 `Danger Zone`
4. 找到 `Change repository visibility`
5. 选择公开
6. 按页面要求确认仓库名并提交

参考:

- [Setting repository visibility](https://docs.github.com/articles/making-a-private-repository-public)

## 我这边当前能不能直接替你改成公开

现在还不能直接代你执行，原因很简单:

- 当前这台机器没有可用的 `gh` CLI
- 当前会话里提供的 GitHub 工具可以读仓库、写文件、提 PR
- 但没有直接修改仓库 visibility 的接口

所以这一步最稳的是你在 GitHub 网页端点一次。
