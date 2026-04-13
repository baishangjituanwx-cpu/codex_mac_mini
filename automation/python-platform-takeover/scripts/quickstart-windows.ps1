param(
  [string]$Platform = "wechat_channels",
  [string]$PackagePath = "configs/content-package.local.yaml",
  [int]$Port = 9222,
  [string]$ProfileDir = "",
  [string]$UrlContains = "",
  [switch]$NoStartBrowser
)

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $PSScriptRoot

function Get-UrlHint {
  param([string]$PlatformName)

  switch ($PlatformName) {
    "wechat_channels" { return "channels.weixin.qq.com" }
    "kuaishou" { return "cp.kuaishou.com" }
    "toutiao" { return "mp.toutiao.com" }
    "weibo" { return "weibo.com" }
    "baijiahao" { return "baijiahao.baidu.com" }
    "zhihu" { return "zhuanlan.zhihu.com" }
    "douyin" { return "creator.douyin.com" }
    default { return "" }
  }
}

if (-not $ProfileDir) {
  $ProfileDir = Join-Path $HOME ".codex-chrome-takeover"
}

if (-not $UrlContains) {
  $UrlContains = Get-UrlHint -PlatformName $Platform
}

Push-Location $projectDir
try {
  if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
      & py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
      & python -m venv .venv
    } else {
      throw "Python 3.10+ was not found."
    }
  }

  $pythonExe = ".\.venv\Scripts\python.exe"
  & $pythonExe -m ensurepip --upgrade
  & $pythonExe -m pip install -e ".[dev]"
  & $pythonExe -m playwright install chromium
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "playwright install chromium failed. Continue with your existing Chrome session, then rerun this step later if needed."
  }

  if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
  }

  if (-not (Test-Path $PackagePath)) {
    $packageDir = Split-Path -Parent $PackagePath
    if ($packageDir) {
      New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
    }
    Copy-Item "configs\content-package.demo.yaml" $PackagePath
  }

  if (-not $NoStartBrowser) {
    & ".\scripts\start-chrome-cdp.ps1" -Port $Port -ProfileDir $ProfileDir
    Start-Sleep -Seconds 2
  }

  Write-Output ""
  Write-Output "== Doctor =="
  $doctorArgs = @("doctor", "--package", $PackagePath, "--platform", $Platform)
  if (-not $NoStartBrowser) {
    $doctorArgs += "--check-browser"
  }
  & ".\scripts\social-publisher.ps1" @doctorArgs

  Write-Output ""
  Write-Output "== Inspect Tabs =="
  $inspectArgs = @("inspect-tabs", "--platform", $Platform, "--package", $PackagePath)
  if ($UrlContains) {
    $inspectArgs += @("--url-contains", $UrlContains)
  }
  & ".\scripts\social-publisher.ps1" @inspectArgs

  Write-Output ""
  Write-Output "== Safe Publish Preview =="
  & ".\scripts\social-publisher.ps1" publish $Platform $PackagePath

  Write-Output ""
  Write-Output "Next:"
  Write-Output "1. Edit $PackagePath and replace the placeholder asset paths."
  Write-Output "2. Log in to the target backend in the CDP browser window."
  Write-Output "3. Re-run inspect-tabs until the right draft tab appears."
  Write-Output "4. Run: .\scripts\social-publisher.ps1 publish $Platform $PackagePath --execute"
} finally {
  Pop-Location
}
