param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js was not found. Install Node.js 18+ first."
}

$nodeVersion = & node -p "process.versions.node"
$nodeMajor = [int]($nodeVersion.Split('.')[0])
if ($nodeMajor -lt 18) {
  throw "Node.js 18+ is required for dashboard-sync."
}

Push-Location $projectDir
try {
  & node scripts/dashboard-doctor.js @CliArgs
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }

  & node scripts/dashboard-sync-review.js @CliArgs
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
