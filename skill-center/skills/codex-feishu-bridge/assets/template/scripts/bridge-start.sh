#!/bin/zsh
set -euo pipefail
LABEL="com.codex.feishu-bridge"
PLIST_SRC="__INSTALL_DIR__/launchd/${LABEL}.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
DOMAIN="gui/$(id -u)"
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"
pkill -f 'node src/bridge.js' >/dev/null 2>&1 || true
pkill -f 'lark-cli event \+subscribe' >/dev/null 2>&1 || true
if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
  launchctl bootout "${DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
fi
launchctl bootstrap "$DOMAIN" "$PLIST_DST"
launchctl enable "${DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
launchctl kickstart -k "${DOMAIN}/${LABEL}"
launchctl print "${DOMAIN}/${LABEL}" | sed -n '1,80p'
