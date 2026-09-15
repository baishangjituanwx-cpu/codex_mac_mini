#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js was not found. Install Node.js 18+ first." >&2
  exit 1
fi

if ! node -e 'const major=Number(process.versions.node.split(".")[0]||"0"); process.exit(major >= 18 ? 0 : 1)'; then
  echo "Node.js 18+ is required for dashboard-sync." >&2
  exit 1
fi

cd "$PROJECT_DIR"
node scripts/dashboard-doctor.js "$@"
exec node scripts/dashboard-sync-review.js "$@"
