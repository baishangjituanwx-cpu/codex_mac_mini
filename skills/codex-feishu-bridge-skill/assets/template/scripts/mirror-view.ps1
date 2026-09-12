param(
  [string]$Target = "latest",
  [int]$Count = 60
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
if (-not $nodeCommand) {
  $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
}
if ($nodeCommand) {
  $nodeExe = $nodeCommand.Path
} else {
  $fallback = Join-Path $HOME ".local\bin\node.exe"
  if (-not (Test-Path $fallback)) {
    throw "node not found on PATH and $fallback is missing."
  }
  $nodeExe = $fallback
}

& $nodeExe (Join-Path $scriptDir "mirror-view.js") $Target $Count
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
