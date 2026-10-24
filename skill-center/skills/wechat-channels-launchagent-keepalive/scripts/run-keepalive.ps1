param(
  [string]$CdpUrl = "",
  [string]$TargetUrl = "https://channels.weixin.qq.com/platform/post/list",
  [double]$WaitSeconds = 4,
  [double]$TimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "wechat_channels_keepalive.py"
$cwdVenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
$activeVenvPython = if ($env:VIRTUAL_ENV) {
  Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
} else {
  ""
}

if (-not $CdpUrl) {
  if ($env:BROWSER_CDP_URL) {
    $CdpUrl = $env:BROWSER_CDP_URL
  } else {
    $CdpUrl = "http://127.0.0.1:9222"
  }
}

if (Test-Path $cwdVenvPython) {
  $pythonExe = $cwdVenvPython
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('playwright') else 1)")
} elseif ($activeVenvPython -and (Test-Path $activeVenvPython)) {
  $pythonExe = $activeVenvPython
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('playwright') else 1)")
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonExe = "py"
  $pythonArgs = @("-3", $scriptPath)
  $versionArgs = @("-3", "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-3", "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('playwright') else 1)")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonExe = (Get-Command python).Path
  $pythonArgs = @($scriptPath)
  $versionArgs = @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
  $dependencyArgs = @("-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('playwright') else 1)")
} else {
  throw "No usable Python executable was found. Create a .venv, activate one, or install Python 3.10+."
}

& $pythonExe @versionArgs
if ($LASTEXITCODE -ne 0) {
  throw "Python 3.10+ is required for the keepalive helper."
}

& $pythonExe @dependencyArgs
if ($LASTEXITCODE -ne 0) {
  throw "Missing Playwright for the keepalive helper. Install it in the active Python environment first."
}

& $pythonExe @pythonArgs "--cdp-url" $CdpUrl "--target-url" $TargetUrl "--wait-seconds" "$WaitSeconds" "--timeout-seconds" "$TimeoutSeconds"
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
