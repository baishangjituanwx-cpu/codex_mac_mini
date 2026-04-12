param(
  [int]$Port = 9222,
  [string]$ProfileDir = "",
  [string]$BrowserPath = ""
)

$ErrorActionPreference = "Stop"

function Get-BrowserExecutable {
  param([string]$PreferredPath)

  if ($PreferredPath) {
    if (Test-Path $PreferredPath) {
      return [System.IO.Path]::GetFullPath($PreferredPath)
    }
    throw "BrowserPath does not exist: $PreferredPath"
  }

  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:LocalAppData\Microsoft\Edge\Application\msedge.exe"
  ) | Where-Object { $_ -and (Test-Path $_) }

  if ($candidates) {
    return $candidates[0]
  }

  throw "Chrome or Edge was not found. Pass -BrowserPath explicitly."
}

if (-not $ProfileDir) {
  $ProfileDir = Join-Path $HOME ".codex-chrome-takeover"
}

$browserExe = Get-BrowserExecutable -PreferredPath $BrowserPath
New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null

$arguments = @(
  "--remote-debugging-port=$Port",
  "--user-data-dir=$ProfileDir"
)

$process = Start-Process -FilePath $browserExe -ArgumentList $arguments -PassThru

Write-Output "Started browser: $browserExe"
Write-Output "PID: $($process.Id)"
Write-Output "CDP endpoint: http://127.0.0.1:$Port"
Write-Output "Profile dir: $ProfileDir"
Write-Output "Log in to the target platform backends in this browser, then keep the takeover tabs open."
