[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs = @()
)

$launcher = Join-Path $PSScriptRoot "invoke_xyq_script.ps1"
& $launcher "submit_run.py" @ScriptArgs
exit $LASTEXITCODE
