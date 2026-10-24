#!/bin/zsh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v node >/dev/null 2>&1; then
  NODE_BIN="node"
elif [ -x "$HOME/.local/bin/node" ]; then
  NODE_BIN="$HOME/.local/bin/node"
else
  echo "node not found" >&2
  exit 1
fi
exec "$NODE_BIN" "$SCRIPT_DIR/mirror-view.js" "${1:-latest}" "${2:-60}"
