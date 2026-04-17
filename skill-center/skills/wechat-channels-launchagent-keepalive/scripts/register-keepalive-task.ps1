param(
  [string]$TaskName = "CodexWeChatChannelsKeepalive",
  [string]$CdpUrl = "",
  [int]$IntervalMinutes = 40
)

$ErrorActionPreference = "Stop"
$launcherPath = Join-Path $PSScriptRoot "run-keepalive.ps1"

if (-not $CdpUrl) {
  if ($env:BROWSER_CDP_URL) {
    $CdpUrl = $env:BROWSER_CDP_URL
  } else {
    $CdpUrl = "http://127.0.0.1:9222"
  }
}

if ($IntervalMinutes -lt 5) {
  throw "IntervalMinutes must be at least 5."
}

$trigger = New-ScheduledTaskTrigger -Once (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
  -RepetitionDuration (New-TimeSpan -Days 3650)

$actionArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$launcherPath`" -CdpUrl `"$CdpUrl`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -Description "Codex WeChat Channels keepalive tab refresh via CDP" `
  -Force | Out-Null

Write-Host "Registered scheduled task: $TaskName"
Write-Host "Launcher: $launcherPath"
Write-Host "CDP URL: $CdpUrl"
