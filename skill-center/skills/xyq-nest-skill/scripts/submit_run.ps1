param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$helper = Join-Path $PSScriptRoot "invoke_xyq_script.ps1"
& $helper -ScriptName "submit_run.py" -ScriptArgs $CliArgs
exit $LASTEXITCODE
