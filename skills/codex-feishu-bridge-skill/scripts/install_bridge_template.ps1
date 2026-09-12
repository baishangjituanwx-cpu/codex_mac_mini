$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillDir = Split-Path -Parent $scriptDir
$templateDir = Join-Path $skillDir "assets\template"
$targetDir = if ($args.Count -gt 0 -and $args[0]) {
  [System.IO.Path]::GetFullPath($args[0])
} else {
  Join-Path $HOME ".codex-feishu-bridge"
}

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
Copy-Item -Path (Join-Path $templateDir "*") -Destination $targetDir -Recurse -Force

$envFile = Join-Path $targetDir ".bridge.env"
$exampleEnvFile = Join-Path $targetDir ".bridge.env.example"
if (-not (Test-Path $envFile) -and (Test-Path $exampleEnvFile)) {
  Copy-Item -Path $exampleEnvFile -Destination $envFile -Force
}

$replaceExtensions = @(".sh", ".command", ".plist")
Get-ChildItem -Path $targetDir -Recurse -File | Where-Object {
  $replaceExtensions -contains $_.Extension
} | ForEach-Object {
  $content = Get-Content -Path $_.FullName -Raw
  $content = $content.Replace("__INSTALL_DIR__", $targetDir)
  [System.IO.File]::WriteAllText($_.FullName, $content, [System.Text.UTF8Encoding]::new($false))
}

Write-Output "Installed bridge template to: $targetDir"
Write-Output "Next steps:"
Write-Output "1. cd `"$targetDir`""
Write-Output "2. npm install"
Write-Output "3. .\node_modules\@larksuite\cli\bin\lark-cli.exe config init --app-id <APP_ID> --app-secret-stdin --brand feishu"
Write-Output "4. .\node_modules\@larksuite\cli\bin\lark-cli.exe auth login --domain im,event --recommend"
Write-Output "5. Confirm the Feishu push target chat id, then run .\scripts\configure_notify_target.ps1 <CHAT_ID>"
Write-Output "   You can also set it from Feishu later by sending /setnotifyhere and /setprogresshere in the target chat."
Write-Output "6. .\scripts\bridge-start.ps1"
