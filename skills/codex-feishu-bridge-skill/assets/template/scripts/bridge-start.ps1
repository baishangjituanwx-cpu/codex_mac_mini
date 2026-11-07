$ErrorActionPreference = "Stop"

function Get-PowerShellExecutable {
  foreach ($candidate in @("pwsh.exe", "pwsh", "powershell.exe", "powershell")) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) {
      return $command.Path
    }
  }
  throw "PowerShell executable not found on PATH."
}

$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root ".codex-feishu-bridge"
$pidFile = Join-Path $dataDir "bridge.pid"
$runScript = Join-Path $PSScriptRoot "run-bridge.ps1"
$stdoutLog = Join-Path $root "bridge.stdout.log"
$stderrLog = Join-Path $root "bridge.stderr.log"

New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

if (Test-Path $pidFile) {
  & (Join-Path $PSScriptRoot "bridge-stop.ps1") | Out-Null
}

$shell = Get-PowerShellExecutable
$process = Start-Process `
  -FilePath $shell `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runScript) `
  -WorkingDirectory $root `
  -WindowStyle Hidden `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -PassThru

[System.IO.File]::WriteAllText(
  $pidFile,
  [string]$process.Id,
  [System.Text.UTF8Encoding]::new($false)
)

Start-Sleep -Seconds 2
if ($process.HasExited) {
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
  throw "Bridge exited immediately. Check bridge.stderr.log."
}

Write-Output "Started bridge host process: $($process.Id)"
& (Join-Path $PSScriptRoot "bridge-status.ps1")
