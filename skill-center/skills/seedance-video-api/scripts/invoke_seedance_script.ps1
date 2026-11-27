param(
  [Parameter(Mandatory = $true)]
  [string]$ScriptName,
  [string[]]$ScriptArgs = @()
)

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot $ScriptName
if (-not (Test-Path $scriptPath)) {
  throw "Script not found: $scriptPath"
}

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

$seen = @{}
$candidates = New-Object System.Collections.Generic.List[object]

function Add-Candidate {
  param(
    [string]$Executable,
    [string[]]$PrefixArgs = @()
  )

  if (-not $Executable) {
    return
  }
  $key = "$Executable|$($PrefixArgs -join ' ')"
  if ($seen.ContainsKey($key)) {
    return
  }
  $seen[$key] = $true
  $candidates.Add(@{
    Executable = $Executable
    PrefixArgs = $PrefixArgs
  })
}

if (Test-Path $cwdVenvPython) {
  Add-Candidate -Executable $cwdVenvPython
}
if ($activeVenvPython -and (Test-Path $activeVenvPython)) {
  Add-Candidate -Executable $activeVenvPython
}
if (Get-Command py -ErrorAction SilentlyContinue) {
  Add-Candidate -Executable "py" -PrefixArgs @("-3")
}
if (Get-Command python -ErrorAction SilentlyContinue) {
  Add-Candidate -Executable (Get-Command python).Path
}
if (Get-Command python3 -ErrorAction SilentlyContinue) {
  Add-Candidate -Executable (Get-Command python3).Path
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
  foreach ($version in @("3.11", "3.10")) {
    try {
      $uvPython = (& uv python find $version 2>$null | Select-Object -First 1).Trim()
    } catch {
      $uvPython = ""
    }
    if ($uvPython -and (Test-Path $uvPython)) {
      Add-Candidate -Executable $uvPython
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

& $selected.Executable @($selected.PrefixArgs + $scriptPath + $ScriptArgs)
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
