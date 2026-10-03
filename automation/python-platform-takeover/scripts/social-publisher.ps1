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
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-c", "import importlib.util, sys; missing=[name for name in ('typer','yaml','playwright') if importlib.util.find_spec(name) is None]; raise SystemExit(0 if not missing else 1)")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonExe = "py"
  $pythonArgs = @("-3", "-m", "social_publisher")
  $versionArgs = @("-3", "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-3", "-c", "import importlib.util, sys; missing=[name for name in ('typer','yaml','playwright') if importlib.util.find_spec(name) is None]; raise SystemExit(0 if not missing else 1)")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonExe = (Get-Command python).Path
  $pythonArgs = @("-m", "social_publisher")
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-c", "import importlib.util, sys; missing=[name for name in ('typer','yaml','playwright') if importlib.util.find_spec(name) is None]; raise SystemExit(0 if not missing else 1)")
} else {
  throw "No usable Python executable was found. Create .venv first or install Python 3."
}

& $pythonExe @versionArgs
if ($LASTEXITCODE -ne 0) {
  throw "Python 3.10+ is required for social-publisher. Install Python 3.10 or create the project's .venv first."
}

& $pythonExe @dependencyArgs
if ($LASTEXITCODE -ne 0) {
  throw "Missing Python dependencies for social-publisher. Run the README install steps first."
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
