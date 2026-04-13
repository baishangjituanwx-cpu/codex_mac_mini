$ErrorActionPreference = "Stop"

function Get-NodeExecutable {
  $nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
  if (-not $nodeCommand) {
    $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
  }
  if ($nodeCommand) {
    return $nodeCommand.Path
  }
  $fallback = Join-Path $HOME ".local\bin\node.exe"
  if (Test-Path $fallback) {
    return $fallback
  }
  throw "node not found on PATH and $fallback is missing."
}

function Parse-EnvValue {
  param([string]$Value)

  $trimmed = $Value.Trim()
  if ($trimmed.StartsWith('"') -and $trimmed.EndsWith('"')) {
    try {
      return $trimmed | ConvertFrom-Json
    } catch {
      return $trimmed.Trim('"')
    }
  }
  if ($trimmed.StartsWith("'") -and $trimmed.EndsWith("'")) {
    return $trimmed.Substring(1, $trimmed.Length - 2)
  }
  return $trimmed
}

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".bridge.env"

if (Test-Path $envFile) {
  foreach ($line in Get-Content -Path $envFile) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$') {
      $name = $matches[1]
      $value = Parse-EnvValue -Value $matches[2]
      Set-Item -Path "Env:$name" -Value $value
    }
  }
}

$nodeExe = Get-NodeExecutable
Push-Location $root
try {
  & $nodeExe "src/bridge.js"
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
} finally {
  Pop-Location
}
