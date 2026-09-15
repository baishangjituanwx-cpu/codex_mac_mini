[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs = @()
)

$launcher = Join-Path $PSScriptRoot "invoke_xyq_script.ps1"
& $launcher "upload_file.py" @ScriptArgs
exit $LASTEXITCODE
