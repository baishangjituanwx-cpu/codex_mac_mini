#!/bin/zsh
set -euo pipefail
LABEL="com.codex.feishu-bridge"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl bootout "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || true
pkill -f 'node src/bridge.js' >/dev/null 2>&1 || true
pkill -f 'lark-cli event \+subscribe' >/dev/null 2>&1 || true
rm -f "$PLIST_DST"
pgrep -af 'node src/bridge.js|lark-cli event \+subscribe' || true
