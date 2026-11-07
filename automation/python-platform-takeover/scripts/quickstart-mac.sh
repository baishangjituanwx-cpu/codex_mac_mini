#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_PATH="configs/content-package.local.yaml"
PLATFORM="wechat_channels"
PORT=9222
PROFILE_DIR="${HOME}/.codex-chrome-takeover"
START_BROWSER=1
URL_CONTAINS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --package)
      PACKAGE_PATH="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --profile-dir)
      PROFILE_DIR="$2"
      shift 2
      ;;
    --url-contains)
      URL_CONTAINS="$2"
      shift 2
      ;;
    --no-start-browser)
      START_BROWSER=0
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

platform_url_hint() {
  case "$1" in
    wechat_channels) echo "channels.weixin.qq.com" ;;
    kuaishou) echo "cp.kuaishou.com" ;;
    toutiao) echo "mp.toutiao.com" ;;
    weibo) echo "weibo.com" ;;
    baijiahao) echo "baijiahao.baidu.com" ;;
    zhihu) echo "zhuanlan.zhihu.com" ;;
    douyin) echo "creator.douyin.com" ;;
    *) echo "" ;;
  esac
}

if [[ -z "$URL_CONTAINS" ]]; then
  URL_CONTAINS="$(platform_url_hint "$PLATFORM")"
fi

cd "$PROJECT_DIR"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

PYTHON_EXE="$PROJECT_DIR/.venv/bin/python"
"$PYTHON_EXE" -m ensurepip --upgrade
"$PYTHON_EXE" -m pip install -e '.[dev]'
if ! "$PYTHON_EXE" -m playwright install chromium; then
  echo "Warning: playwright install chromium failed. Continue with your existing Chrome session, then rerun this step later if needed." >&2
fi

if [[ ! -f ".env" ]]; then
  cp .env.example .env
fi

if [[ ! -f "$PACKAGE_PATH" ]]; then
  mkdir -p "$(dirname "$PACKAGE_PATH")"
  cp configs/content-package.demo.yaml "$PACKAGE_PATH"
fi

if [[ $START_BROWSER -eq 1 ]]; then
  "$PROJECT_DIR/scripts/start-chrome-cdp.sh" --port "$PORT" --profile-dir "$PROFILE_DIR"
  sleep 2
fi

echo ""
echo "== Doctor =="
DOCTOR_ARGS=(doctor --package "$PACKAGE_PATH" --platform "$PLATFORM")
if [[ $START_BROWSER -eq 1 ]]; then
  DOCTOR_ARGS+=(--check-browser)
fi
"$PROJECT_DIR/scripts/social-publisher.sh" "${DOCTOR_ARGS[@]}"

echo ""
echo "== Inspect Tabs =="
if [[ -n "$URL_CONTAINS" ]]; then
  "$PROJECT_DIR/scripts/social-publisher.sh" inspect-tabs --platform "$PLATFORM" --package "$PACKAGE_PATH" --url-contains "$URL_CONTAINS"
else
  "$PROJECT_DIR/scripts/social-publisher.sh" inspect-tabs --platform "$PLATFORM" --package "$PACKAGE_PATH"
fi

echo ""
echo "== Safe Publish Preview =="
"$PROJECT_DIR/scripts/social-publisher.sh" publish "$PLATFORM" "$PACKAGE_PATH"

echo ""
echo "Next:"
echo "1. Edit $PACKAGE_PATH and replace the placeholder asset paths."
echo "2. Log in to the target backend in the CDP browser window."
echo "3. Re-run inspect-tabs until the right draft tab appears."
echo "4. Run: ./scripts/social-publisher.sh publish $PLATFORM $PACKAGE_PATH --execute"
