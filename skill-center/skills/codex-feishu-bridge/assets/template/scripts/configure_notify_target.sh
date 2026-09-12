#!/bin/zsh
set -euo pipefail
ROOT="__INSTALL_DIR__"
ENV_FILE="$ROOT/.bridge.env"
TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  printf "Enter Feishu chat id to receive publish-success notifications: "
  read -r TARGET
fi

if [ -z "$TARGET" ]; then
  echo "No chat id provided." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  cp "$ROOT/.bridge.env.example" "$ENV_FILE"
fi

python3 - "$ENV_FILE" "$TARGET" <<'PY'
from pathlib import Path
import json, sys
env_path = Path(sys.argv[1])
target = sys.argv[2]
lines = env_path.read_text().splitlines() if env_path.exists() else []
needle = "CODEX_BRIDGE_PUBLISH_NOTIFY_CHAT_ID="
newline = f'{needle}{json.dumps(target, ensure_ascii=False)}'
found = False
out = []
for line in lines:
    if line.startswith(needle):
        out.append(newline)
        found = True
    else:
        out.append(line)
if not found:
    out.append(newline)
env_path.write_text("\n".join(out) + "\n")
PY

echo "Updated publish notify chat id: $TARGET"
echo "If the bridge is already running, restart it with:"
echo "  zsh \"$ROOT/scripts/bridge-start.sh\""
