#!/usr/bin/env bash

set -euo pipefail

PORT=9222
PROFILE_DIR="${HOME}/.codex-chrome-takeover"
BROWSER_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --profile-dir)
      PROFILE_DIR="$2"
      shift 2
      ;;
    --browser-path)
      BROWSER_PATH="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

find_browser() {
  if [[ -n "$BROWSER_PATH" ]]; then
    if [[ -x "$BROWSER_PATH" ]]; then
      printf '%s\n' "$BROWSER_PATH"
      return 0
    fi
    echo "Browser path does not exist: $BROWSER_PATH" >&2
    exit 1
  fi

  local candidates=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    "/usr/bin/google-chrome"
    "/usr/bin/chromium"
    "/usr/bin/chromium-browser"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "Chrome or Edge was not found. Pass --browser-path explicitly." >&2
  exit 1
}

BROWSER_EXE="$(find_browser)"
mkdir -p "$PROFILE_DIR"

if [[ "$OSTYPE" == darwin* && "$BROWSER_EXE" == *.app/Contents/MacOS/* ]]; then
  APP_BUNDLE="${BROWSER_EXE%/Contents/MacOS/*}.app"
  nohup open -na "$APP_BUNDLE" --args \
    "--remote-debugging-port=${PORT}" \
    "--user-data-dir=${PROFILE_DIR}" \
    >/dev/null 2>&1 &
else
  nohup "$BROWSER_EXE" \
    "--remote-debugging-port=${PORT}" \
    "--user-data-dir=${PROFILE_DIR}" \
    >/dev/null 2>&1 &
fi

for _ in $(seq 1 15); do
  if curl -fsS "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    echo "Started browser: $BROWSER_EXE"
    echo "CDP endpoint: http://127.0.0.1:${PORT}"
    echo "Profile dir: $PROFILE_DIR"
    echo "Log in to the target platform backends in this browser, then keep the takeover tabs open."
    exit 0
  fi
  sleep 1
done

echo "Browser launch was attempted, but CDP did not become reachable on port ${PORT}." >&2
echo "Close any conflicting Chrome/Edge instances for this profile, then retry." >&2
exit 1
