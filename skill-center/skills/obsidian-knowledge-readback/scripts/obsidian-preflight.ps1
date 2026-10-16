[CmdletBinding()]
param(
  [switch]$Manifest,
  [string]$Query,
  [string]$Read
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sshKey = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".ssh\id_ed25519_obsidian_bridge"
$sshTarget = "BSJT@192.168.1.10"
$sshPort = "22"

function Show-Usage {
  Write-Error "Usage: .\obsidian-preflight.ps1 -Manifest | -Query 'keywords' | -Read 'Codex/note.md'"
}

$selectedModeCount = 0
if ($Manifest.IsPresent) { $selectedModeCount++ }
if (-not [string]::IsNullOrWhiteSpace($Query)) { $selectedModeCount++ }
if (-not [string]::IsNullOrWhiteSpace($Read)) { $selectedModeCount++ }

if ($selectedModeCount -gt 1) {
  Show-Usage
  exit 2
}

if (-not (Test-Path -LiteralPath $sshKey -PathType Leaf)) {
  throw "Obsidian preflight failed: SSH key is not readable: $sshKey"
}

$ssh = Get-Command ssh.exe -ErrorAction SilentlyContinue
if ($null -eq $ssh) {
  throw "Obsidian preflight failed: OpenSSH client ssh.exe was not found. Install Windows OpenSSH Client first."
}

function ConvertTo-PosixSingleQuoted {
  param([Parameter(Mandatory = $true)][string]$Value)

  $escaped = $Value.Replace("'", "'\''")
  return "'" + $escaped + "'"
}

function Invoke-RemoteBash {
  param(
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$Argument
  )

  $remoteCommand = "bash -s"
  if ($PSBoundParameters.ContainsKey("Argument")) {
    $remoteCommand += " -- " + (ConvertTo-PosixSingleQuoted -Value $Argument)
  }

  $sshArgs = @(
    "-i", $sshKey,
    "-p", $sshPort,
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=10",
    $sshTarget,
    $remoteCommand
  )

  $Script | & $ssh.Path @sshArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Obsidian preflight failed: remote SSH command exited with code $LASTEXITCODE"
  }
}

if ($selectedModeCount -eq 0 -or $Manifest.IsPresent) {
  $remoteScript = @'
set -euo pipefail
vault="/vol1/1000/Obsidian/obsidian-vault"
if [[ ! -d "$vault" ]]; then
  echo "Obsidian preflight failed: Vault does not exist: $vault" >&2
  exit 1
fi

find "$vault" -type f -name '*.md' -size -5M \
  -not -path '*/.*/*' -print0 |
while IFS= read -r -d '' file; do
  relative="${file#"$vault"/}"
  title="$(sed -n -E 's/^title:[[:space:]]*//p; s/^#[[:space:]]+//p' "$file" | head -n 1)"
  [[ -n "$title" ]] || title="(untitled)"
  mtime="$(stat -c '%y' "$file" 2>/dev/null || true)"
  printf '%s\t%s\t%s\n' "$relative" "$title" "$mtime"
done | sort
'@
  Invoke-RemoteBash -Script $remoteScript
  exit 0
}

if (-not [string]::IsNullOrWhiteSpace($Read)) {
  $remoteScript = @'
set -euo pipefail
vault="/vol1/1000/Obsidian/obsidian-vault"
relative="${1:-}"

case "$relative" in
  ""|/*|.*|*/.*|*..*)
    echo "Obsidian preflight failed: only relative Markdown paths inside the Vault are allowed" >&2
    exit 1
    ;;
esac

case "$relative" in
  *.md)
    ;;
  *)
    echo "Obsidian preflight failed: only Markdown files may be read" >&2
    exit 1
    ;;
esac

vault_real="$(realpath -e -- "$vault")"
target="$(realpath -e -- "$vault/$relative")"
case "$target" in
  "$vault_real"/*)
    ;;
  *)
    echo "Obsidian preflight failed: target is outside the Vault" >&2
    exit 1
    ;;
esac

if [[ ! -f "$target" || "${target##*.}" != "md" ]]; then
  echo "Obsidian preflight failed: target is not a readable Markdown file" >&2
  exit 1
fi

size="$(stat -c '%s' "$target")"
if (( size > 200000 )); then
  echo "Obsidian preflight failed: note exceeds 200KB; refusing one-shot read" >&2
  exit 1
fi

sed -n '1,500p' "$target"
'@
  Invoke-RemoteBash -Script $remoteScript -Argument $Read
  exit 0
}

$remoteScript = @'
set -euo pipefail
vault="/vol1/1000/Obsidian/obsidian-vault"
query="${1:-}"
if [[ ! -d "$vault" ]]; then
  echo "Obsidian preflight failed: Vault does not exist: $vault" >&2
  exit 1
fi

find "$vault" -type f -name '*.md' -size -5M \
  -not -path '*/.*/*' -print0 |
while IFS= read -r -d '' file; do
  if grep -Fqi -- "$query" "$file"; then
    relative="${file#"$vault"/}"
    title="$(sed -n -E 's/^title:[[:space:]]*//p; s/^#[[:space:]]+//p' "$file" | head -n 1)"
    [[ -n "$title" ]] || title="(untitled)"
    match="$(grep -Fi -m 1 -- "$query" "$file" | tr '\t\r\n' '   ' | cut -c 1-240 || true)"
    printf '%s\t%s\t%s\n' "$relative" "$title" "$match"
  fi
done | sort
'@
Invoke-RemoteBash -Script $remoteScript -Argument $Query
