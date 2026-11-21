[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs = @()
)

$launcher = Join-Path $PSScriptRoot "invoke_xyq_script.ps1"
& $launcher "download_results.py" @ScriptArgs
exit $LASTEXITCODE
