#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script_path="$script_dir/seedance_cli.py"
cwd_venv_python="$(pwd)/.venv/bin/python"
active_venv_python="${VIRTUAL_ENV:-}/bin/python"
python_exe=""

version_ok() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
}

declare -a candidates=()

if [[ -x "$cwd_venv_python" ]]; then
  candidates+=("$cwd_venv_python")
fi
if [[ -n "${VIRTUAL_ENV:-}" && -x "$active_venv_python" ]]; then
  candidates+=("$active_venv_python")
fi
if command -v python3 >/dev/null 2>&1; then
  candidates+=("$(command -v python3)")
fi
if command -v python >/dev/null 2>&1; then
  candidates+=("$(command -v python)")
fi
if command -v uv >/dev/null 2>&1; then
  while IFS= read -r uv_python; do
    if [[ -n "$uv_python" && -x "$uv_python" ]]; then
      candidates+=("$uv_python")
    fi
  done < <(
    {
      uv python find 3.11 2>/dev/null || true
      uv python find 3.10 2>/dev/null || true
    } | awk '!seen[$0]++'
  )
fi

for candidate in "${candidates[@]}"; do
  if version_ok "$candidate"; then
    python_exe="$candidate"
    break
  fi
done

if [[ -z "$python_exe" ]]; then
  echo "No usable Python 3.10+ executable was found. Create a .venv, activate one, install Python 3.10+, or install a uv-managed Python." >&2
  exit 1
fi

exec "$python_exe" "$script_path" "$@"
