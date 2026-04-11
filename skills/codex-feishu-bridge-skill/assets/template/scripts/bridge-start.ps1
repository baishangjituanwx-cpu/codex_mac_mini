param(
    [switch]$RegisterStartupTask
)

$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
$TaskName = "CodexFeishuBridge"
$RunScript = Join-Path $Root "scripts\run-bridge.ps1"

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*src\\bridge.js*" -or
    $_.CommandLine -like "*src/bridge.js*" -or
    $_.CommandLine -like "*lark-cli*event*subscribe*"
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

if ($RegisterStartupTask) {
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RunScript`""
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Codex Feishu Bridge" -Force | Out-Null
}

Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $RunScript) -WindowStyle Hidden
Start-Sleep -Seconds 2
& (Join-Path $Root "scripts\bridge-status.ps1")
