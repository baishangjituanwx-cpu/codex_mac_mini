param(
    [string]$Target
)

$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
$EnvFile = Join-Path $Root ".bridge.env"

if (-not $Target) {
    $Target = Read-Host "Enter Feishu chat id to receive publish-success notifications"
}

if (-not $Target) {
    throw "No chat id provided."
}

if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $Root ".bridge.env.example") $EnvFile
}

$Needle = "CODEX_BRIDGE_PUBLISH_NOTIFY_CHAT_ID="
$NewLine = $Needle + '"' + $Target + '"'
$Lines = @()
if (Test-Path $EnvFile) {
    $Lines = Get-Content $EnvFile
}

$Found = $false
$Output = foreach ($Line in $Lines) {
    if ($Line.StartsWith($Needle)) {
        $Found = $true
        $NewLine
    } else {
        $Line
    }
}
if (-not $Found) {
    $Output += $NewLine
}

Set-Content -Path $EnvFile -Value $Output -Encoding UTF8
Write-Host "Updated publish notify chat id: $Target"
Write-Host "If the bridge is already running, restart it with:"
Write-Host "  powershell -ExecutionPolicy Bypass -File `"$Root\scripts\bridge-start.ps1`""
