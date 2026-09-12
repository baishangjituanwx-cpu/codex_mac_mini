#!/bin/zsh
set -euo pipefail
LABEL="com.codex.feishu-bridge"
echo "== launchd =="
launchctl print "gui/$(id -u)/${LABEL}" | sed -n '1,80p' || true
echo
echo "== processes =="
pgrep -af 'node src/bridge.js|lark-cli event \+subscribe' || true
echo
echo "== recent bridge log =="
tail -n 30 "__INSTALL_DIR__/bridge.log" || true
