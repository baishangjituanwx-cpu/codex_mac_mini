# INSTALL QUICKSTART

Use this file when another Codex instance is asked to install the bridge on a fresh machine.

## Goal

Install the `codex-feishu-bridge` skill and deploy the runnable Feishu bridge service on the current machine.

## Assumptions

- `Codex.app` is already installed.
- `codex` CLI is already logged in.
- The operator can provide Feishu `App ID` and `App Secret`.
- The machine is macOS and can use `launchctl`.

## Minimal execution path

1. Place the skill directory at:

```text
~/.codex/skills/codex-feishu-bridge
```

2. Deploy the runnable bridge template:

```bash
bash ~/.codex/skills/codex-feishu-bridge/scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
```

3. Install dependencies:

```bash
cd "$HOME/.codex-feishu-bridge"
npm install
```

4. Ask the operator for Feishu `App ID` and `App Secret`, then configure `lark-cli`:

```bash
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

5. Run Feishu login:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
```

6. Verify auth:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth status
```

7. Re-confirm notify targets:

```bash
./scripts/configure_notify_target.sh <CHAT_ID>
```

Or later in Feishu:

```text
/setnotifyhere
/setprogresshere
```

8. Start the service:

```bash
./scripts/bridge-start.sh
```

9. Verify:

```bash
./scripts/bridge-status.sh
```

## Smoke test

In Feishu:

```text
/status
/threads
```

Then send one normal text message and confirm:

- the bot replies
- `.codex-feishu-bridge/mirrors/` contains mirror files

## Operator-facing note

If any step would restart Codex or disrupt the bridge workflow, stop and ask for explicit confirmation first.
