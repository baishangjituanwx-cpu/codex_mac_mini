$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Join-Path (Split-Path -Parent $ScriptDir) "skills"
$TargetDir = Join-Path $HOME ".codex\skills"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
robocopy $SourceDir $TargetDir /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null

$robocopyCode = $LASTEXITCODE
if ($robocopyCode -ge 8) {
    throw "robocopy failed with exit code $robocopyCode"
}

Write-Host "Synced skill mirror to $TargetDir"
