param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"

function Resolve-NodeCommand {
  $candidates = @("node", "node.exe")
  foreach ($candidate in $candidates) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) {
      return $command.Source
    }
  }

  throw "Node.js was not found in PATH. Install Node.js and retry."
}

$node = Resolve-NodeCommand
$scriptPath = Join-Path $PSScriptRoot "huice-push-distribution-order.js"
& $node $scriptPath @CliArgs
exit $LASTEXITCODE
