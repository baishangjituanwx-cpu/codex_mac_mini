param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"
$helper = Join-Path $PSScriptRoot "invoke_seedance_script.ps1"
& $helper -ScriptName "seedance_cli.py" -ScriptArgs $CliArgs
exit $LASTEXITCODE
