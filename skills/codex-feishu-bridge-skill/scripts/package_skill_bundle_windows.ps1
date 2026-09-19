param(
    [string]$OutFile
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $OutFile) {
    $OutFile = Join-Path (Split-Path -Parent $Root) "codex-feishu-bridge-skill-windows.zip"
}

if (Test-Path $OutFile) {
    Remove-Item $OutFile -Force
}

Compress-Archive -Path $Root -DestinationPath $OutFile -Force
Write-Host "Created: $OutFile"
