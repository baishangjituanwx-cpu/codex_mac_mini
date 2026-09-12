param(
  [int]$Lines = 80
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$bridgeLog = Join-Path $root "bridge.log"

if (-not (Test-Path $bridgeLog)) {
  throw "bridge.log not found at $bridgeLog"
}

Get-Content -Path $bridgeLog -Tail $Lines
