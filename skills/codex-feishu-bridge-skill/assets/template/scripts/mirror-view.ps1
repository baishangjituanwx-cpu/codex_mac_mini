param(
    [string]$ThreadName = "latest",
    [int]$Lines = 60
)

$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
$MirrorDir = Join-Path $Root ".codex-feishu-bridge\mirrors"
if (-not (Test-Path $MirrorDir)) {
    throw "Mirror directory not found: $MirrorDir"
}

if ($ThreadName -eq "latest") {
    $File = Get-ChildItem $MirrorDir -Filter *.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1
} else {
    $File = Get-ChildItem $MirrorDir -Filter "$ThreadName*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

if (-not $File) {
    throw "No mirror file found."
}

Get-Content $File.FullName -Tail $Lines
