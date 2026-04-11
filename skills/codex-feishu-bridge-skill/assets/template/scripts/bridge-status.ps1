$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
$TaskName = "CodexFeishuBridge"

Write-Host "== scheduled task =="
Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Format-List TaskName, State, Author
Write-Host ""
Write-Host "== processes =="
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*src\\bridge.js*" -or
    $_.CommandLine -like "*src/bridge.js*" -or
    $_.CommandLine -like "*lark-cli*event*subscribe*"
} | Select-Object ProcessId, Name, CommandLine | Format-List
Write-Host ""
Write-Host "== recent bridge log =="
if (Test-Path (Join-Path $Root "bridge.log")) {
    Get-Content (Join-Path $Root "bridge.log") -Tail 30
}
