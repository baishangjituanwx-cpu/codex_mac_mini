#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

REMOTE_HOST="${MEMPALACE_REMOTE_HOST:-root@8.219.193.109}"
REMOTE_BASE="${MEMPALACE_REMOTE_BASE:-/srv/mempalace}"
REMOTE_PALACE="${MEMPALACE_REMOTE_PALACE:-${REMOTE_BASE}/palace}"
REMOTE_IMPORT_DIR="${MEMPALACE_REMOTE_IMPORT_DIR:-${REMOTE_BASE}/imports/$(basename "${REPO_ROOT}")}"
REMOTE_RUN_AS="${MEMPALACE_REMOTE_RUN_AS:-mempalace}"
PASSWORD_FILE="${MEMPALACE_SSH_PASSWORD_FILE:-${HOME}/.codex/secrets/mempalace-remote-ssh.password}"
WING="${MEMPALACE_WING:-$(basename "${REPO_ROOT}")}"

VERIFY_QUERY=""
SKIP_SEARCH=0
DRY_RUN=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Incrementally sync this repository to the remote MemPalace host, then re-mine
only changed files on the server. Deleted local files are purged from the
remote mirror and from the remote palace.

Options:
  --query TEXT      Run a verification search after syncing
  --skip-search     Skip verification search output
  --dry-run         Show what rsync would do, then stop
  -h, --help        Show this help

Environment overrides:
  MEMPALACE_REMOTE_HOST
  MEMPALACE_REMOTE_BASE
  MEMPALACE_REMOTE_PALACE
  MEMPALACE_REMOTE_IMPORT_DIR
  MEMPALACE_REMOTE_RUN_AS
  MEMPALACE_SSH_PASSWORD_FILE
  MEMPALACE_WING
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query)
      [[ $# -ge 2 ]] || { echo "Missing value for --query" >&2; exit 1; }
      VERIFY_QUERY="$2"
      shift 2
      ;;
    --skip-search)
      SKIP_SEARCH=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require_cmd ssh
require_cmd sshpass
require_cmd rsync

if [[ ! -r "${PASSWORD_FILE}" ]]; then
  echo "Missing password file: ${PASSWORD_FILE}" >&2
  exit 1
fi

SSH_BASE=(
  sshpass -f "${PASSWORD_FILE}"
  ssh
  -o StrictHostKeyChecking=accept-new
  -o PreferredAuthentications=password
  -o PubkeyAuthentication=no
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=3
  -o LogLevel=ERROR
  "${REMOTE_HOST}"
)

RSYNC_RSH=(
  sshpass -f "${PASSWORD_FILE}"
  ssh
  -o StrictHostKeyChecking=accept-new
  -o PreferredAuthentications=password
  -o PubkeyAuthentication=no
  -o LogLevel=ERROR
)

run_remote() {
  "${SSH_BASE[@]}" "$@"
}

run_remote_as_user() {
  local remote_script="$1"
  local quoted_script
  printf -v quoted_script '%q' "${remote_script}"
  run_remote "sudo -u '${REMOTE_RUN_AS}' -H bash -lc ${quoted_script}"
}

RSYNC_ARGS=(
  -rlptDz
  --delete
  --delete-excluded
  --progress
  "--filter=P /mempalace.yaml"
  "--filter=P /entities.json"
  --exclude=.git/
  --exclude=.venv/
  --exclude=venv/
  --exclude=env/
  --exclude=__pycache__/
  --exclude=node_modules/
  --exclude=.next/
  --exclude=dist/
  --exclude=build/
  --exclude=coverage/
  --exclude=.cache/
  --exclude=.mypy_cache/
  --exclude=.pytest_cache/
  --exclude=.ruff_cache/
  --exclude=.tox/
  --exclude=.nox/
  --exclude=.idea/
  --exclude=.vscode/
  --exclude=.ipynb_checkpoints/
  --exclude=.codex-skill-monitor-snapshot.txt
  -e "$(printf '%q ' "${RSYNC_RSH[@]}")"
)

if [[ ${DRY_RUN} -eq 1 ]]; then
  RSYNC_ARGS+=(--dry-run)
fi

echo "Sync source: ${REPO_ROOT}"
echo "Remote host: ${REMOTE_HOST}"
echo "Remote repo: ${REMOTE_IMPORT_DIR}"
echo "Wing:        ${WING}"

run_remote "mkdir -p '${REMOTE_IMPORT_DIR}' '${REMOTE_PALACE}'"

rsync \
  "${RSYNC_ARGS[@]}" \
  "${REPO_ROOT}/" \
  "${REMOTE_HOST}:${REMOTE_IMPORT_DIR}/"

if [[ ${DRY_RUN} -eq 1 ]]; then
  echo
  echo "Dry run complete. No remote mine executed."
  exit 0
fi

run_remote "chown -R '${REMOTE_RUN_AS}:${REMOTE_RUN_AS}' '${REMOTE_IMPORT_DIR}'"

read -r -d '' REMOTE_CLEANUP <<'PY' || true
import os
from mempalace.palace import get_closets_collection, get_collection

palace_path = os.environ["PALACE_PATH"]
wing = os.environ["WING"]
collection = get_collection(palace_path)
closets = get_closets_collection(palace_path)

stale = []
seen = set()
offset = 0
batch_size = 500

while True:
    batch = collection.get(
        where={"wing": wing},
        limit=batch_size,
        offset=offset,
        include=["metadatas"],
    )
    ids = batch.get("ids") or []
    if not ids:
        break
    for meta in batch.get("metadatas") or []:
        source_file = (meta or {}).get("source_file")
        if not source_file or source_file in seen:
            continue
        seen.add(source_file)
        if not os.path.exists(source_file):
            stale.append(source_file)
    offset += batch_size

for source_file in stale:
    collection.delete(where={"source_file": source_file})
    closets.delete(where={"source_file": source_file})

print(f"Stale source files purged: {len(stale)}")
for source_file in stale[:20]:
    print(f"  - {source_file}")
PY

run_remote_as_user "$(cat <<EOF
cd "${REMOTE_BASE}"
export PALACE_PATH="${REMOTE_PALACE}" WING="${WING}" PYTHONUNBUFFERED=1
source "${REMOTE_BASE}/venv/bin/activate"
python - <<'PY'
${REMOTE_CLEANUP}
PY
EOF
)"

run_remote_as_user "$(cat <<EOF
cd "${REMOTE_IMPORT_DIR}"
export PYTHONUNBUFFERED=1
source "${REMOTE_BASE}/venv/bin/activate"
mempalace init "${REMOTE_IMPORT_DIR}" --yes
mempalace --palace "${REMOTE_PALACE}" mine "${REMOTE_IMPORT_DIR}" --wing "${WING}"
EOF
)"

if [[ ${SKIP_SEARCH} -eq 0 && -n "${VERIFY_QUERY}" ]]; then
  printf -v VERIFY_QUERY_Q '%q' "${VERIFY_QUERY}"
  echo
  echo "Verification search: ${VERIFY_QUERY}"
  run_remote_as_user "$(cat <<EOF
cd "${REMOTE_BASE}"
export PYTHONUNBUFFERED=1
source "${REMOTE_BASE}/venv/bin/activate"
mempalace --palace "${REMOTE_PALACE}" search ${VERIFY_QUERY_Q} --wing "${WING}" --results 5
EOF
)"
fi

echo
echo "Remote MemPalace sync finished."
