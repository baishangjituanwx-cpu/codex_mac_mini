[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Text,

    [Parameter(Mandatory = $true)]
    [string]$IdempotencyKey,

    [string]$ChatId = "oc_45f4f2c2f0a783f636969cd821179f40",

    [string]$Profile = "legacy-a958",

    [ValidateSet("bot", "user")]
    [string]$As = "bot"
)

$ErrorActionPreference = "Stop"

function Resolve-LarkCli {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $candidates = @(
        (Join-Path $RepoRoot "node_modules\.bin\lark-cli.cmd"),
        (Join-Path $RepoRoot "node_modules\@larksuite\cli\bin\lark-cli.exe"),
        (Join-Path $RepoRoot "node_modules\@larksuite\cli\bin\lark-cli.cmd")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    $globalCommand = Get-Command -Name "lark-cli" -ErrorAction SilentlyContinue
    if ($globalCommand) {
        return $globalCommand.Source
    }

    return $null
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
$larkCli = Resolve-LarkCli -RepoRoot $repoRoot

if (-not $larkCli) {
    Write-Error "Unable to locate lark-cli. Install it under the repo node_modules or add lark-cli to PATH."
}

$arguments = @(
    "--profile", $Profile,
    "im", "+messages-send",
    "--as", $As,
    "--chat-id", $ChatId,
    "--idempotency-key", $IdempotencyKey,
    "--text", $Text
)

& $larkCli @arguments
exit $LASTEXITCODE
