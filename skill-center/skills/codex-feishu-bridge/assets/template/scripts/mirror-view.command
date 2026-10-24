#!/bin/zsh
set -euo pipefail
cd "__INSTALL_DIR__"
zsh "__INSTALL_DIR__/scripts/mirror-view.sh" "${1:-latest}" "${2:-60}"
printf "\nPress Enter to close..."
read -r
