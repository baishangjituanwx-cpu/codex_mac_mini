param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"
$helper = Join-Path $PSScriptRoot "invoke_seedance_script.ps1"
& $helper -ScriptName "init_cover_package.py" -ScriptArgs $ScriptArgs
exit $LASTEXITCODE
