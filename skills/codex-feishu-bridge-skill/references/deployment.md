# Deployment Guide

## Scope

This guide deploys the Feishu-to-Codex bridge onto a target macOS or Windows machine as a user-scoped local service.

## Prerequisites

- macOS user account with access to `launchctl`, or a Windows user account with PowerShell available on `PATH`
- `Codex.app` installed and `codex` CLI already logged in
- Node.js available either on `PATH` or under `~/.local/bin/node`
- A Feishu self-built app with bot capability enabled
- Feishu bot event subscription configured for `im.message.receive_v1`
- Feishu `App ID` and `App Secret`

## Recommended install path

- macOS: `~/.codex-feishu-bridge`
- Windows: `%USERPROFILE%\.codex-feishu-bridge`

This keeps the bridge isolated from user workspaces and avoids path issues from folders containing spaces.

## Deployment steps

1. Copy the skill directory to the target machine.
2. Run the installer.

macOS:

```bash
bash <skill-dir>/scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
```

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-dir>\scripts\install_bridge_template.ps1" "$HOME\.codex-feishu-bridge"
```

3. Change into the deployed directory.

macOS:

```bash
cd "$HOME/.codex-feishu-bridge"
```

Windows PowerShell:

```powershell
Set-Location "$HOME\.codex-feishu-bridge"
```

4. Install dependencies.

```bash
npm install
```

5. Configure Feishu CLI app credentials.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

Pipe the `App Secret` through stdin instead of placing it on the command line.

6. Authenticate Feishu CLI.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe auth login --domain im,event --recommend
```

7. Verify auth.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth status
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe auth status
```

8. Start the bridge service.

macOS:

```bash
./scripts/bridge-start.sh
```

Windows PowerShell:

```powershell
.\scripts\bridge-start.ps1
```

Before or after starting the bridge, re-confirm the push target chat for publish-success notifications:

macOS:

```bash
./scripts/configure_notify_target.sh <CHAT_ID>
```

Windows PowerShell:

```powershell
.\scripts\configure_notify_target.ps1 <CHAT_ID>
```

Or, once the bot is reachable in the desired Feishu chat, send:

```text
/setnotifyhere
/setprogresshere
```

9. Verify service state.

macOS:

```bash
./scripts/bridge-status.sh
```

Windows PowerShell:

```powershell
.\scripts\bridge-status.ps1
```

## Service behavior

macOS:

- Label: `com.codex.feishu-bridge`
- Plist path: `~/Library/LaunchAgents/com.codex.feishu-bridge.plist`
- Bridge restarts automatically if it exits

Windows:

- The bridge is launched by `bridge-start.ps1` as a detached per-user PowerShell host.
- Runtime PID file: `.codex-feishu-bridge\bridge.pid`
- Use `bridge-stop.ps1` before reinstalling or when rotating credentials.

## Files created at runtime

- `.codex-feishu-bridge/state.json`
- `.codex-feishu-bridge/mirrors/*.md`
- `.codex-feishu-bridge/mirrors/*.jsonl`
- `.codex-feishu-bridge/bridge.pid` on Windows
- `bridge.log`
- `bridge.stdout.log`
- `bridge.stderr.log`

## Optional publish-monitor tuning

The bridge can watch one or more local Codex threads and auto-push a completion summary to Feishu when a publish run finishes successfully.

Useful environment variables:

- `CODEX_BRIDGE_PUBLISH_NOTIFY_CHAT_ID`
  Target Feishu chat id for completion pushes. Re-confirm this on each new installation.
- `CODEX_BRIDGE_PROGRESS_NOTIFY_CHAT_ID`
  Target Feishu chat id for live task-progress pushes. Re-confirm this on each new installation.
- `CODEX_BRIDGE_MONITOR_THREAD_NAMES`
  Comma-separated thread-name patterns to monitor.
- `CODEX_BRIDGE_PUBLISH_SUCCESS_KEYWORDS`
  Comma-separated success phrases. Auto-push only happens when the latest result text contains one of them.

Default success phrases include:

```text
发布成功,已发布,完成发布,发布完成
```

## Post-install smoke test

1. Send a bot message to a known Feishu private chat.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli im +messages-send --as bot --chat-id <CHAT_ID> --text "bridge online"
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe im +messages-send --as bot --chat-id <CHAT_ID> --text "bridge online"
```

2. In Feishu, run:

```text
/status
/threads
```

3. Confirm a mirror file is created after the first inbound message.
4. On Windows, double-click `scripts\mirror-view.cmd` or run `.\scripts\mirror-view.ps1 latest 60` to inspect the mirrored conversation locally.

## Restart-sensitive step

If the operator needs to restart Codex or do any action that disrupts the current bridge workflow, pause and get explicit confirmation first.
