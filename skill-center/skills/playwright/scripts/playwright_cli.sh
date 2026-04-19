#!/usr/bin/env bash
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required but not found on PATH." >&2
  exit 1
fi

# Homebrew Node can miss local trust roots that curl already uses.
# Reuse a readable CA bundle when the user has not supplied one.
if [[ -z "${NODE_EXTRA_CA_CERTS:-}" ]]; then
  for cafile in \
    /etc/ssl/cert.pem \
    /opt/homebrew/etc/openssl@3/cert.pem \
    /usr/local/etc/openssl@3/cert.pem
  do
    if [[ -r "$cafile" ]]; then
      export NODE_EXTRA_CA_CERTS="$cafile"
      break
    fi
  done
fi

# Optional native rebuilds like fsevents are not required for CLI usage
# and can hang on first-run package bootstrap.
if [[ -z "${NPM_CONFIG_IGNORE_SCRIPTS:-}" ]]; then
  export NPM_CONFIG_IGNORE_SCRIPTS=true
fi

# Playwright CLI uses Unix sockets for sessions. Shorten TMPDIR on macOS so
# session socket paths stay under the platform limit.
if [[ -z "${TMPDIR:-}" || ${#TMPDIR} -gt 40 ]]; then
  short_tmp="/tmp/pwcli"
  mkdir -p "$short_tmp"
  export TMPDIR="$short_tmp"
fi

has_session_flag="false"
for arg in "$@"; do
  case "$arg" in
    --session|--session=*)
      has_session_flag="true"
      break
      ;;
  esac
done

cmd=(npx --yes --package @playwright/cli playwright-cli)
if [[ "${has_session_flag}" != "true" && -n "${PLAYWRIGHT_CLI_SESSION:-}" ]]; then
  cmd+=(--session "${PLAYWRIGHT_CLI_SESSION}")
fi
cmd+=("$@")

exec "${cmd[@]}"
