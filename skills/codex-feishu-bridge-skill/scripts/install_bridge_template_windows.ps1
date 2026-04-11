param(
    [string]$TargetDir = "C:\codex-feishu-bridge"
)

$ErrorActionPreference = "Stop"
$SkillDir = Split-Path -Parent $PSScriptRoot
$TemplateDir = Join-Path $SkillDir "assets\template"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Copy-Item -Path (Join-Path $TemplateDir "*") -Destination $TargetDir -Recurse -Force
Copy-Item -Path (Join-Path $TemplateDir ".bridge.env.example") -Destination (Join-Path $TargetDir ".bridge.env.example") -Force

$EnvFile = Join-Path $TargetDir ".bridge.env"
if (-not (Test-Path $EnvFile) -and (Test-Path (Join-Path $TargetDir ".bridge.env.example"))) {
    Copy-Item (Join-Path $TargetDir ".bridge.env.example") $EnvFile
}

$Extensions = @(".ps1", ".cmd", ".js", ".json", ".sh", ".command", ".md", ".plist")
Get-ChildItem -Path $TargetDir -Recurse -File | Where-Object {
    $Extensions -contains $_.Extension -or $_.Name -eq "package.json"
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content.Replace("__INSTALL_DIR__", $TargetDir)
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}

Write-Host "Installed bridge template to: $TargetDir"
Write-Host "Next steps:"
Write-Host "1. cd $TargetDir"
Write-Host "2. npm install"
Write-Host "3. .\node_modules\.bin\lark-cli.cmd config init --app-id <APP_ID> --app-secret-stdin --brand feishu"
Write-Host "4. .\node_modules\.bin\lark-cli.cmd auth login --domain im,event --recommend"
Write-Host "5. .\scripts\configure_notify_target.ps1 <CHAT_ID>"
Write-Host "6. .\scripts\bridge-start.ps1"
