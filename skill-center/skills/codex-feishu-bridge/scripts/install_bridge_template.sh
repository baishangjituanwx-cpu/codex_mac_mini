#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${1:-$HOME/.codex-feishu-bridge}"
TEMPLATE_DIR="$SKILL_DIR/assets/template"

mkdir -p "$TARGET_DIR"
rsync -a "$TEMPLATE_DIR/" "$TARGET_DIR/"

if [ ! -f "$TARGET_DIR/.bridge.env" ] && [ -f "$TARGET_DIR/.bridge.env.example" ]; then
  cp "$TARGET_DIR/.bridge.env.example" "$TARGET_DIR/.bridge.env"
fi

find "$TARGET_DIR" -type f \
  \( -name "*.sh" -o -name "*.command" -o -name "*.plist" -o -name "*.js" -o -name "package.json" \) \
  -print0 | while IFS= read -r -d '' file; do
    perl -0pi -e "s|__INSTALL_DIR__|$TARGET_DIR|g" "$file"
  done

chmod +x "$TARGET_DIR"/scripts/*.sh "$TARGET_DIR"/scripts/*.command

if [ -t 0 ] && [ -t 1 ]; then
  printf "Configure publish notify chat id now? [y/N] "
  read -r answer
  case "${answer:l}" in
    y|yes)
      "$TARGET_DIR/scripts/configure_notify_target.sh"
      ;;
  esac
fi

printf "Installed bridge template to: %s\n" "$TARGET_DIR"
printf "Next steps:\n"
printf "1. cd %s\n" "$TARGET_DIR"
printf "2. npm install\n"
printf "3. ./node_modules/@larksuite/cli/bin/lark-cli config init --app-id <APP_ID> --app-secret-stdin --brand feishu\n"
printf "4. ./node_modules/@larksuite/cli/bin/lark-cli auth login --domain im,event --recommend\n"
printf "5. Confirm the Feishu push target chat id, then run ./scripts/configure_notify_target.sh <CHAT_ID>\n"
printf "   You can also set it from Feishu later by sending /setnotifyhere in the target chat.\n"
printf "6. ./scripts/bridge-start.sh\n"
