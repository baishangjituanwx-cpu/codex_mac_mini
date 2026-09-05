$ErrorActionPreference = "Stop"

function Get-ChildProcessIds {
  param([int]$ParentId)

  $children = @(
    Get-CimInstance Win32_Process -Filter "ParentProcessId = $ParentId" -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty ProcessId
  )
  $all = @()
  foreach ($childId in $children) {
    $all += $childId
    $all += Get-ChildProcessIds -ParentId $childId
  }
  return $all
}

$root = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $root ".codex-feishu-bridge\bridge.pid"
$candidateIds = @()

if (Test-Path $pidFile) {
  try {
    $candidateIds += [int](Get-Content -Path $pidFile -Raw).Trim()
  } catch {
  }
}

if (-not $candidateIds) {
  $candidateIds = @(
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
      Where-Object {
        $_.CommandLine -like "*$root*" -and (
          $_.CommandLine -like "*run-bridge.ps1*" -or
          $_.CommandLine -like "*src\\bridge.js*"
        )
      } |
      Select-Object -ExpandProperty ProcessId -Unique
  )
}

$processTree = @()
foreach ($id in $candidateIds | Sort-Object -Unique) {
  $processTree += Get-ChildProcessIds -ParentId $id
  $processTree += $id
}

$processTree = $processTree | Sort-Object -Descending -Unique
foreach ($id in $processTree) {
  Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
}

Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue

if ($processTree) {
  Write-Output ("Stopped process ids: " + ($processTree -join ", "))
} else {
  Write-Output "No bridge process found."
}
