param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
  $pythonExe = $venvPython
  $pythonArgs = @("-m", "social_publisher")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonExe = "py"
  $pythonArgs = @("-3", "-m", "social_publisher")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonExe = (Get-Command python).Path
  $pythonArgs = @("-m", "social_publisher")
} else {
  throw "No usable Python executable was found. Create .venv first or install Python 3."
}

Push-Location $projectDir
try {
  & $pythonExe @pythonArgs @CliArgs
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
