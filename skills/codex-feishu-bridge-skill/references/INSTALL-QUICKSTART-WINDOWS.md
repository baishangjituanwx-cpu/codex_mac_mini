# Windows Quickstart

## 1. Install bridge template

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_bridge_template_windows.ps1 -TargetDir C:\codex-feishu-bridge
cd C:\codex-feishu-bridge
```

## 2. Install dependencies

```powershell
npm install
```

## 3. Configure Feishu credentials

```powershell
.\node_modules\.bin\lark-cli.cmd config init --app-id <APP_ID> --app-secret-stdin --brand feishu
```

## 4. Authenticate

```powershell
.\node_modules\.bin\lark-cli.cmd auth login --domain im,event --recommend
```

## 5. Set notify target

```powershell
.\scripts\configure_notify_target.ps1 <CHAT_ID>
```

## 6. Start bridge

```powershell
.\scripts\bridge-start.ps1
```

## 7. Optional auto-start

```powershell
.\scripts\bridge-start.ps1 -RegisterStartupTask
```

## 8. Check status

```powershell
.\scripts\bridge-status.ps1
```
