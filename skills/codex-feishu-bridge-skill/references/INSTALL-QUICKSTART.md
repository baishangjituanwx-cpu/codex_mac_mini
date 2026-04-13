# INSTALL QUICKSTART

Use this file when another Codex instance is asked to install the bridge on a fresh machine.

## Goal

Install the `codex-feishu-bridge` skill and deploy the runnable Feishu bridge service on the current machine.

## Assumptions

- `Codex.app` is already installed.
- `codex` CLI is already logged in.
- The operator can provide Feishu `App ID` and `App Secret`.
- The machine is either:
  - macOS with `launchctl`
  - Windows with PowerShell available on `PATH`

## Minimal execution path

1. Place the skill directory at:

```text
~/.codex/skills/codex-feishu-bridge
```

2. Deploy the runnable bridge template.

macOS:

```bash
bash ~/.codex/skills/codex-feishu-bridge/scripts/install_bridge_template.sh "$HOME/.codex-feishu-bridge"
```

Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$HOME\.codex\skills\codex-feishu-bridge\scripts\install_bridge_template.ps1" "$HOME\.codex-feishu-bridge"
```

3. Install dependencies.

macOS:

```bash
cd "$HOME/.codex-feishu-bridge"
npm install
```

Windows PowerShell:

```powershell
Set-Location "$HOME\.codex-feishu-bridge"
npm install
```

4. Ask the operator for Feishu `App ID` and `App Secret`, then configure `lark-cli`.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

5. Run Feishu login.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe auth login --domain im,event --recommend
```

6. Verify auth.

macOS:

```bash
./node_modules/@larksuite/cli/bin/lark-cli auth status
```

Windows PowerShell:

```powershell
.\node_modules\@larksuite\cli\bin\lark-cli.exe auth status
```

7. Re-confirm notify targets.

macOS:

```bash
./scripts/configure_notify_target.sh <CHAT_ID>
```

Windows PowerShell:

```powershell
.\scripts\configure_notify_target.ps1 <CHAT_ID>
```

Or later in Feishu:

```text
/setnotifyhere
/setprogresshere
```

8. Start the service.

macOS:

```bash
./scripts/bridge-start.sh
```

Windows PowerShell:

```powershell
.\scripts\bridge-start.ps1
```

9. Verify.

macOS:

```bash
./scripts/bridge-status.sh
```

Windows PowerShell:

```powershell
.\scripts\bridge-status.ps1
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
- on Windows, `.\scripts\mirror-view.cmd` can open the latest mirrored conversation in a double-clickable console window

## Operator-facing note

If any step would restart Codex or disrupt the bridge workflow, stop and ask for explicit confirmation first.
