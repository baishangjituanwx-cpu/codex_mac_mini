# Deployment Guide

## Scope

This guide deploys the Feishu-to-Codex bridge onto a target macOS machine as a user-scoped service.

## Prerequisites

- macOS user account with access to `launchctl`
- `Codex.app` installed and `codex` CLI already logged in
- Node.js available either on `PATH` or under `~/.local/bin/node`
- A Feishu self-built app with bot capability enabled
- Feishu bot event subscription configured for `im.message.receive_v1`
- Feishu `App ID` and `App Secret`

## Recommended install path

```text
~/.codex-feishu-bridge
```

This keeps the bridge isolated from user workspaces and avoids path issues from folders containing spaces.

## Deployment steps

1. Copy the skill directory to the target machine.
2. Run the installer:

```bash
bash <skill-dir>/scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
```

3. Change into the deployed directory:

```bash
cd "$HOME/.codex-feishu-bridge"
```

4. Install dependencies:

```bash
npm install
```

5. Configure Feishu CLI app credentials:

```bash
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

Pipe the `App Secret` through stdin instead of placing it on the command line.

6. Authenticate Feishu CLI:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
```

7. Verify auth:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth status
```

8. Start the bridge service:

```bash
./scripts/bridge-start.sh
```

Before or after starting the bridge, re-confirm the push target chat for publish-success notifications:

```bash
./scripts/configure_notify_target.sh <CHAT_ID>
```

Or, once the bot is reachable in the desired Feishu chat, send:

```text
/setnotifyhere
/setprogresshere
```

9. Verify service state:

```bash
./scripts/bridge-status.sh
```

## Launchd behavior

- Label: `com.codex.feishu-bridge`
- Plist path: `~/Library/LaunchAgents/com.codex.feishu-bridge.plist`
- Bridge restarts automatically if it exits

## Files created at runtime

- `.codex-feishu-bridge/state.json`
- `.codex-feishu-bridge/mirrors/*.md`
- `.codex-feishu-bridge/mirrors/*.jsonl`
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

1. Send a bot message to a known Feishu private chat:

```bash
./node_modules/@larksuite/cli/bin/lark-cli im +messages-send --as bot --chat-id <CHAT_ID> --text "bridge online"
```

2. In Feishu, run:

```text
/status
/threads
```

3. Confirm a mirror file is created after the first inbound message.

## Restart-sensitive step

If the operator needs to restart Codex or do any action that disrupts the current bridge workflow, pause and get explicit confirmation first.
