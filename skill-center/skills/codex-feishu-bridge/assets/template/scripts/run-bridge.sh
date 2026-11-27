#!/bin/zsh
set -euo pipefail
cd "__INSTALL_DIR__"
if [ -f "__INSTALL_DIR__/.bridge.env" ]; then
  set -a
  source "__INSTALL_DIR__/.bridge.env"
  set +a
fi
if command -v node >/dev/null 2>&1; then
  exec node src/bridge.js
fi
if [ -x "$HOME/.local/bin/node" ]; then
  exec "$HOME/.local/bin/node" src/bridge.js
fi
echo "node not found on PATH and ~/.local/bin/node is missing" >&2
exit 1
