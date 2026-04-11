param(
    [int]$Lines = 80
)

$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
Get-Content (Join-Path $Root "bridge.log") -Tail $Lines
