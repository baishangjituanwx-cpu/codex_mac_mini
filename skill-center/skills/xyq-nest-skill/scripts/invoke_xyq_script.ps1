[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ScriptName,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs = @()
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir $ScriptName

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    Write-Error "Python script not found: $scriptPath"
}

function Test-PythonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [string[]]$PrefixArgs = @()
    )

    if (-not [string]::IsNullOrWhiteSpace($Executable)) {
        $command = Get-Command -Name $Executable -ErrorAction SilentlyContinue
        if (-not $command) {
            return $null
        }
    }

    $versionCheck = @(
        "-c",
        "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)"
    )

    try {
        & $Executable @PrefixArgs @versionCheck | Out-Null
        if ($LASTEXITCODE -eq 0) {
            return @{
                Executable = $Executable
                PrefixArgs = $PrefixArgs
            }
        }
    }
    catch {
        return $null
    }

    return $null
}

$candidates = @()
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
$repoPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $repoPython -PathType Leaf) {
    $candidates += @{ Executable = $repoPython; PrefixArgs = @() }
}

if ($env:VIRTUAL_ENV) {
    $venvPython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
        $candidates += @{ Executable = $venvPython; PrefixArgs = @() }
    }
}

$candidates += @(
    @{ Executable = "py"; PrefixArgs = @("-3") },
    @{ Executable = "python"; PrefixArgs = @() },
    @{ Executable = "python3"; PrefixArgs = @() }
)

$selected = $null
foreach ($candidate in $candidates) {
    $result = Test-PythonCommand -Executable $candidate.Executable -PrefixArgs $candidate.PrefixArgs
    if ($result) {
        $selected = $result
        break
    }
}

if (-not $selected) {
    Write-Error "Python 3.9+ not found. Install Python or create .venv before running this launcher."
}

& $selected.Executable @($selected.PrefixArgs) $scriptPath @ScriptArgs
exit $LASTEXITCODE
