#!/bin/zsh
set -euo pipefail
tail -n "${1:-80}" "__INSTALL_DIR__/bridge.log"
