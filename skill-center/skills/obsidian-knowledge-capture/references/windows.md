# Windows 使用说明

该技能的知识提取和写入策略在 macOS 与 Windows 上保持一致。Windows 侧只需要替换本地技能路径、SSH 私钥路径和预检命令；远端 Vault 仍是 Linux 路径。

## 本地路径与预检

同步 `skill-center` 后，技能目录通常位于:

```text
%USERPROFILE%\.codex\skills\obsidian-knowledge-capture\
```

写入前复用 `obsidian-knowledge-readback` 的 Windows 只读入口执行清单、关键词检索和受限 Markdown 回读:

```powershell
$preflight = Join-Path $env:USERPROFILE ".codex\skills\obsidian-knowledge-readback\scripts\obsidian-preflight.ps1"
powershell.exe -ExecutionPolicy Bypass -File $preflight -Manifest
powershell.exe -ExecutionPolicy Bypass -File $preflight -Query "项目约定 知识沉淀"
powershell.exe -ExecutionPolicy Bypass -File $preflight -Read "Codex/Decisions/example.md"
```

SSH 私钥默认位置为 `%USERPROFILE%\.ssh\id_ed25519_obsidian_bridge`。Vault 仍使用远端路径 `/vol1/1000/Obsidian/obsidian-vault`，不要把它改成 Windows 本地路径，也不要把本地绝对路径写入捕获内容。

## 三种模式

- `【立即沉淀】`: 只提取已确认且稳定的事实，完成预检后将写入路由到 allowlist 中的 Codex 线程。
- `【待确认沉淀】`: 在当前回复中生成精简 capture packet；不得写入 Vault。
- `【修订 Obsidian】`: 先用上面的 `-Read` 读取相关笔记，确认精确改动后再路由到 allowlist 中的 Codex 线程。

普通 Windows PowerShell 会话和非 allowlisted Codex 线程均保持只读。该技能不新增本地写 Vault 的 `.ps1` 或 `.cmd` 包装器；写入必须由允许的 Codex 线程执行，并在同一路径回读目标笔记、核对关键内容、等待 `knowledge-bridge` 后才可报告完成。

## 写入范围与回报

远端写入仅允许:

- `Codex/Inbox/`
- `Codex/Decisions/`
- `Codex/Runbooks/`

成功回报必须包含模式、实际 Obsidian 相对路径、是否读取并去重旧笔记、写入/回读结果和桥接同步证据。预检、SSH、目标回读或桥接等待任一步失败时，不得声称知识已持久化。
