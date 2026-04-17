param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "seedance_cli.py"
$cwdVenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
$activeVenvPython = if ($env:VIRTUAL_ENV) {
  Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
} else {
  ""
}

if (Test-Path $cwdVenvPython) {
  $pythonExe = $cwdVenvPython
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
} elseif ($activeVenvPython -and (Test-Path $activeVenvPython)) {
  $pythonExe = $activeVenvPython
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonExe = "py"
  $pythonArgs = @("-3", $scriptPath)
  $versionArgs = @("-3", "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonExe = (Get-Command python).Path
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
} else {
  throw "No usable Python executable was found. Create a .venv, activate one, or install Python 3.10+."
}

& $pythonExe @versionArgs
if ($LASTEXITCODE -ne 0) {
  throw "Python 3.10+ is required for seedance_cli."
}

& $pythonExe @pythonArgs @CliArgs
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
