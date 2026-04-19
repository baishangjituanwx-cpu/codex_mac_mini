# Remote MemPalace Sync

这个仓库已经接到远端 MemPalace 中心主机，可以用下面这条脚本做增量同步:

```bash
bash scripts/sync_remote_mempalace.sh --query "social publisher doctor"
```

## 默认行为

- 把当前仓库同步到远端:
  - `root@8.219.193.109`
  - `/srv/mempalace/imports/multi-platform-content-pipeline`
- 使用远端 palace:
  - `/srv/mempalace/palace`
- 使用 wing:
  - `multi-platform-content-pipeline`
- 复用本机密码文件:
  - `~/.codex/secrets/mempalace-remote-ssh.password`

## 这个脚本会做什么

1. 用 `rsync` 增量同步仓库内容到远端镜像目录
2. 排除高噪音目录和缓存:
   - `.git/`
   - `.venv/` / `venv/`
   - `node_modules/`
   - `dist/` / `build/`
   - `.pytest_cache/` / `.ruff_cache/` / `.mypy_cache/`
   - `.codex-skill-monitor-snapshot.txt`
3. 删除远端镜像里已经不存在的本地文件
4. 清理 palace 里对应的陈旧 drawers / closets
5. 在远端重新执行 `mempalace init`
6. 在远端执行 `mempalace mine`
   - 未改动文件会按 `mtime` 自动跳过
   - 改动过的文件会被重新入库

## 常用命令

只同步并重新入库:

```bash
bash scripts/sync_remote_mempalace.sh
```

同步后顺手验证搜索:

```bash
bash scripts/sync_remote_mempalace.sh --query "skill-change-monitor"
```

先看将要同步什么，不真的改远端:

```bash
bash scripts/sync_remote_mempalace.sh --dry-run
```

## 环境变量覆盖

如果以后远端主机、wing、密码文件或导入目录变了，可以临时覆盖:

```bash
MEMPALACE_REMOTE_HOST="root@your-host" \
MEMPALACE_WING="your-wing" \
bash scripts/sync_remote_mempalace.sh
```

支持的环境变量:

- `MEMPALACE_REMOTE_HOST`
- `MEMPALACE_REMOTE_BASE`
- `MEMPALACE_REMOTE_PALACE`
- `MEMPALACE_REMOTE_IMPORT_DIR`
- `MEMPALACE_REMOTE_RUN_AS`
- `MEMPALACE_SSH_PASSWORD_FILE`
- `MEMPALACE_WING`
