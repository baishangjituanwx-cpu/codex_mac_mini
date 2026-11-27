#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR%/scripts}/skills/"
TARGET_DIR="${HOME}/.codex/skills/"

mkdir -p "${TARGET_DIR}"
rsync -a --delete --exclude '.DS_Store' "${SOURCE_DIR}" "${TARGET_DIR}"

echo "Synced skill mirror to ${TARGET_DIR}"
