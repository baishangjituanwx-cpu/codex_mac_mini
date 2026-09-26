[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs = @()
)

$launcher = Join-Path $PSScriptRoot "invoke_xyq_script.ps1"
& $launcher "get_thread.py" @ScriptArgs
exit $LASTEXITCODE
