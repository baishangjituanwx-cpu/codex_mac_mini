# Skill Center Mirror

这里是当前本机 `~/.codex/skills/` 的仓库镜像版本。

目标只有一个:

- 让 `Mac` 和 `Windows` 都能拿到同一套 skill 内容
- 让 GitHub 仓库里保留一份完整可复制的技能中心

## 当前范围

- 已镜像技能数量: `63`
- 来源: `/Users/baishangjituan/.codex/skills/`
- 未包含:
  - `.system/` 下的系统内置 skill
  - 插件缓存目录里的 skill

这意味着现在仓库里这份技能中心，已经覆盖了你平时真正会直接调用的那批本机 skill。

## 目录

```text
skill-center/
├── README.md
├── scripts/
│   ├── sync-skills.ps1
│   └── sync-skills.sh
├── skills/
│   ├── baijiahao-ops/
│   ├── douyin-ops/
│   ├── kuaishou-ops/
│   ├── social-publish-automation/
│   └── ...
└── skills-manifest.txt
```

## Mac 使用

```bash
cd skill-center
bash scripts/sync-skills.sh
```

执行后会把仓库里的 `skill-center/skills/` 同步到:

```text
~/.codex/skills/
```

## Windows 使用

在 PowerShell 里执行:

```powershell
cd skill-center
powershell -ExecutionPolicy Bypass -File .\scripts\sync-skills.ps1
```

执行后会把仓库里的 `skill-center/skills/` 同步到:

```text
$HOME\.codex\skills\
```

## 同步方式

这两套脚本都按“镜像同步”处理:

- 会更新已有 skill
- 会复制新增 skill
- 会删除目标目录里不在镜像中的旧 skill

这样做的目的，是保证 Mac 和 Windows 的 skill 数量与内容都一致。

## 校验

技能清单见:

- `skill-center/skills-manifest.txt`

比如你刚才点名的这个 skill，也已经会出现在镜像里:

- `skill-center/skills/baijiahao-ops/SKILL.md`
