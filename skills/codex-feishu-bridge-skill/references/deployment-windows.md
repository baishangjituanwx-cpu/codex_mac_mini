# Windows Deployment Guide

## Scope

This guide deploys the Feishu-to-Codex bridge onto a target Windows machine.

## Prerequisites

- Windows 10 or Windows 11
- PowerShell 5.1 or newer
- `Codex` desktop app installed and `codex` CLI already logged in
- Node.js available on `PATH`
- A Feishu self-built app with bot capability enabled
- Feishu bot event subscription configured for `im.message.receive_v1`
- Feishu `App ID` and `App Secret`

## Recommended install path

```text
C:\codex-feishu-bridge
```

Avoid deeply nested paths or folders with many spaces.

## Deployment steps

1. Copy the skill directory to the target machine.
2. Run the Windows installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_bridge_template_windows.ps1 -TargetDir C:\codex-feishu-bridge
```

3. Change into the deployed directory:

```powershell
cd C:\codex-feishu-bridge
```

4. Install dependencies:

```powershell
npm install
```

5. Configure Feishu CLI app credentials:

```powershell
.\node_modules\.bin\lark-cli.cmd config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

6. Authenticate Feishu CLI:

```powershell
.\node_modules\.bin\lark-cli.cmd auth login --domain im,event --recommend
```

7. Verify auth:

```powershell
.\node_modules\.bin\lark-cli.cmd auth status
```

8. Configure the publish notify chat id:

```powershell
.\scripts\configure_notify_target.ps1 <CHAT_ID>
```

Or, once the bot is reachable in the desired Feishu chat, send:

```text
/setnotifyhere
/setprogresshere
```

9. Start the bridge:

```powershell
.\scripts\bridge-start.ps1
```

10. If you want auto-start at logon, register the startup task:

```powershell
.\scripts\bridge-start.ps1 -RegisterStartupTask
```

11. Verify service state:

```powershell
.\scripts\bridge-status.ps1
```

## Runtime files

- `.codex-feishu-bridge\state.json`
- `.codex-feishu-bridge\mirrors\*.md`
- `.codex-feishu-bridge\mirrors\*.jsonl`
- `bridge.log`
- `bridge.stdout.log`
- `bridge.stderr.log`

## Windows behavior

- Normal start uses a hidden PowerShell process
- Optional auto-start uses a user-scoped Scheduled Task
- Restart is manual unless the operator enables the startup task

## Smoke test

1. Send a bot message:

```powershell
.\node_modules\.bin\lark-cli.cmd im +messages-send --as bot --chat-id <CHAT_ID> --text "bridge online"
```

2. In Feishu, run:

```text
/status
/threads
```

3. Confirm a mirror file is created after the first inbound message.
