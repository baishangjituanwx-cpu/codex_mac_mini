#!/usr/bin/env bash
set -euo pipefail

ssh_key="${HOME}/.ssh/id_ed25519_obsidian_bridge"
ssh_target="BSJT@192.168.1.10"
ssh_port="22"

usage() {
  echo "Usage: $0 --manifest | --query \"keywords\" | --read \"Codex/note.md\"" >&2
}

mode="manifest"
query=""
relative_path=""
case "${1:-}" in
  --manifest)
    mode="manifest"
    ;;
  --query)
    if [[ $# -lt 2 || -z "${2:-}" ]]; then
      usage
      exit 2
    fi
    mode="query"
    query="$2"
    ;;
  --read)
    if [[ $# -lt 2 || -z "${2:-}" ]]; then
      usage
      exit 2
    fi
    mode="read"
    relative_path="$2"
    ;;
  *)
    usage
    exit 2
    ;;
esac

if [[ ! -r "$ssh_key" ]]; then
  echo "Obsidian preflight failed: SSH key is not readable: $ssh_key" >&2
  exit 1
fi

if [[ "$mode" == "manifest" ]]; then
  ssh -i "$ssh_key" -p "$ssh_port" \
    -o BatchMode=yes -o ConnectTimeout=10 \
    "$ssh_target" 'bash -s' <<'REMOTE_SCRIPT'
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
REMOTE_SCRIPT
  exit 0
fi

if [[ "$mode" == "read" ]]; then
  printf -v quoted_path '%q' "$relative_path"
  ssh -i "$ssh_key" -p "$ssh_port" \
    -o BatchMode=yes -o ConnectTimeout=10 \
    "$ssh_target" "bash -s -- $quoted_path" <<'REMOTE_SCRIPT'
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
REMOTE_SCRIPT
  exit 0
fi

printf -v quoted_query '%q' "$query"
ssh -i "$ssh_key" -p "$ssh_port" \
  -o BatchMode=yes -o ConnectTimeout=10 \
  "$ssh_target" "bash -s -- $quoted_query" <<'REMOTE_SCRIPT'
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
REMOTE_SCRIPT
