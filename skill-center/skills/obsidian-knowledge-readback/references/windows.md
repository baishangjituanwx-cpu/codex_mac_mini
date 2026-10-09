# Windows 使用说明

该技能通过 Windows 内置 OpenSSH Client 连接远端 Linux Vault。PowerShell 只负责本地入口和参数传递，Vault 仍使用远端 Linux 路径；不要把 `/vol1/1000/Obsidian/obsidian-vault` 改成 Windows 本地路径。

## 前置条件

1. 在“设置 → 系统 → 可选功能”中安装 **OpenSSH Client**，并确认 `ssh.exe` 已在 `PATH` 中。
2. 将桥接私钥放在：

   ```text
   %USERPROFILE%\.ssh\id_ed25519_obsidian_bridge
   ```

3. 确认远端主机 `192.168.1.10:22` 和账号 `BSJT` 可通过 BatchMode SSH 连接。

## 命令

在该技能目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\obsidian-preflight.ps1 -Manifest
powershell -ExecutionPolicy Bypass -File .\scripts\obsidian-preflight.ps1 -Query "项目约定 Windows"
powershell -ExecutionPolicy Bypass -File .\scripts\obsidian-preflight.ps1 -Read "Codex/Decisions/example.md"
```

脚本只允许读取远端 Vault 内的 Markdown 文件，拒绝隐藏目录、绝对路径、路径穿越和超过 200KB 的一次性读取；它不会写入、同步或删除笔记。
