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

function Test-PythonVersion {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Executable,
    [string[]]$PrefixArgs = @()
  )

  & $Executable @PrefixArgs "-c" "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" *> $null
  return $LASTEXITCODE -eq 0
}

$candidates = @()
if (Test-Path $cwdVenvPython) {
  $candidates += @{
    Executable = $cwdVenvPython
    PrefixArgs = @()
  }
}
if ($activeVenvPython -and (Test-Path $activeVenvPython)) {
  $candidates += @{
    Executable = $activeVenvPython
    PrefixArgs = @()
  }
}
if (Get-Command py -ErrorAction SilentlyContinue) {
  $candidates += @{
    Executable = "py"
    PrefixArgs = @("-3")
  }
}
if (Get-Command python -ErrorAction SilentlyContinue) {
  $candidates += @{
    Executable = (Get-Command python).Path
    PrefixArgs = @()
  }
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
  foreach ($version in @("3.11", "3.10")) {
    try {
      $uvPython = (& uv python find $version 2>$null | Select-Object -First 1).Trim()
    } catch {
      $uvPython = ""
    }
    if ($uvPython -and (Test-Path $uvPython)) {
      $candidates += @{
        Executable = $uvPython
        PrefixArgs = @()
      }
    }
  }
}

$selected = $null
foreach ($candidate in $candidates) {
  if (Test-PythonVersion -Executable $candidate.Executable -PrefixArgs $candidate.PrefixArgs) {
    $selected = $candidate
    break
  }
}

if (-not $selected) {
  throw "No usable Python 3.10+ executable was found. Create a .venv, activate one, install Python 3.10+, or install a uv-managed Python."
}

& $selected.Executable @($selected.PrefixArgs + $scriptPath + $CliArgs)
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
