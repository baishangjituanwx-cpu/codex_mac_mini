#!/bin/zsh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
zsh "$SCRIPT_DIR/mirror-view.sh" "${1:-latest}" "${2:-60}"
printf "\nPress Enter to close..."
read -r
