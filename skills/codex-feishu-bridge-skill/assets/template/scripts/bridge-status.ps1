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
$bridgeLog = Join-Path $root "bridge.log"

Write-Output "== bridge host =="
if (Test-Path $pidFile) {
  try {
    $hostPid = [int](Get-Content -Path $pidFile -Raw).Trim()
    $hostProcess = Get-Process -Id $hostPid -ErrorAction Stop
    Write-Output "running: yes"
    Write-Output "pid: $($hostProcess.Id)"
    Write-Output "process: $($hostProcess.ProcessName)"
  } catch {
    Write-Output "running: no"
    Write-Output "message: stale pid file found; remove it or rerun bridge-start.ps1"
  }
} else {
  Write-Output "running: no"
}

Write-Output ""
Write-Output "== process tree =="
if (Test-Path $pidFile) {
  try {
    $hostPid = [int](Get-Content -Path $pidFile -Raw).Trim()
    $treeIds = @(Get-ChildProcessIds -ParentId $hostPid) + $hostPid
    foreach ($id in $treeIds | Sort-Object -Unique) {
      $process = Get-Process -Id $id -ErrorAction SilentlyContinue
      if ($process) {
        Write-Output ("{0} {1}" -f $process.Id, $process.ProcessName)
      }
    }
  } catch {
    Write-Output "No active process tree found."
  }
} else {
  Write-Output "No active process tree found."
}

Write-Output ""
Write-Output "== recent bridge log =="
if (Test-Path $bridgeLog) {
  Get-Content -Path $bridgeLog -Tail 30
} else {
  Write-Output "bridge.log not found."
}
