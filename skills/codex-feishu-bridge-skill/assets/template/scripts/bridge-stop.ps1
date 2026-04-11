param(
    [switch]$UnregisterStartupTask
)

$ErrorActionPreference = "Stop"
$TaskName = "CodexFeishuBridge"

Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*src\\bridge.js*" -or
    $_.CommandLine -like "*src/bridge.js*" -or
    $_.CommandLine -like "*lark-cli*event*subscribe*"
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

if ($UnregisterStartupTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
}
