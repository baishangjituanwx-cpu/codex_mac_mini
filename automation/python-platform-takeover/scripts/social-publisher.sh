#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON_EXE="$VENV_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_EXE="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_EXE="$(command -v python)"
else
  echo "No usable Python executable was found. Create .venv first or install Python 3." >&2
  exit 1
fi

if ! "$PYTHON_EXE" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Python 3.10+ is required for social-publisher." >&2
  exit 1
fi

if ! "$PYTHON_EXE" -c "import importlib.util; missing=[name for name in ('typer','yaml','playwright') if importlib.util.find_spec(name) is None]; raise SystemExit(0 if not missing else 1)"; then
  echo "Missing Python dependencies for social-publisher. Run the README install steps first." >&2
  exit 1
fi

cd "$PROJECT_DIR"
exec "$PYTHON_EXE" -m social_publisher "$@"
