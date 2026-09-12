$ErrorActionPreference = "Stop"

param(
  [string]$Target = ""
)

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".bridge.env"
$exampleFile = Join-Path $root ".bridge.env.example"

if (-not $Target) {
  $Target = Read-Host "Enter Feishu chat id to receive publish-success notifications"
}

if (-not $Target) {
  throw "No chat id provided."
}

if (-not (Test-Path $envFile)) {
  Copy-Item -Path $exampleFile -Destination $envFile -Force
}

$needle = "CODEX_BRIDGE_PUBLISH_NOTIFY_CHAT_ID="
$newLine = $needle + ($Target | ConvertTo-Json -Compress)
$lines = @(Get-Content -Path $envFile -ErrorAction SilentlyContinue)
$found = $false
$output = @()

foreach ($line in $lines) {
  if ($line.StartsWith($needle)) {
    $output += $newLine
    $found = $true
  } else {
    $output += $line
  }
}

if (-not $found) {
  $output += $newLine
}

[System.IO.File]::WriteAllText(
  $envFile,
  (($output -join "`n") + "`n"),
  [System.Text.UTF8Encoding]::new($false)
)

Write-Output "Updated publish notify chat id: $Target"
Write-Output "If the bridge is already running, restart it with:"
Write-Output ('  powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $PSScriptRoot "bridge-start.ps1"))
