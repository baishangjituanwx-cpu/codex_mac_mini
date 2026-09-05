#!/usr/bin/env bash
set -euo pipefail

expected_chat="hermes_agent_mac_mini"
mode="validate-only"
message_file=""
read_stdin="0"
visual_confirmed="0"
activate_lark="0"

usage() {
  cat <<'EOF'
Usage:
  send-hermes-feishu-prompt.sh --expected-chat hermes_agent_mac_mini --validate-only
  send-hermes-feishu-prompt.sh --expected-chat hermes_agent_mac_mini --message-file /path/prompt.txt --paste-only
  printf '%s' "$PROMPT" | send-hermes-feishu-prompt.sh --expected-chat hermes_agent_mac_mini --message-stdin --send
  printf '%s' "$PROMPT" | send-hermes-feishu-prompt.sh --expected-chat hermes_agent_mac_mini --visual-confirmed --message-stdin --send

Modes:
  --validate-only  Verify Feishu is foreground and the visible chat contains expected chat name. No paste/send.
  --paste-only     Paste message into the verified chat input, but do not send.
  --clear-only     Clear the verified chat input, but do not paste/send.
  --send           Paste message into the verified chat input and click Feishu's send button.
  --visual-confirmed
                  Permit paste/send when Codex has just visually confirmed a screenshot shows the expected chat.
  --activate-lark  Bring Lark/Feishu to foreground before validating.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected-chat)
      expected_chat="${2:-}"
      shift 2
      ;;
    --message-file)
      message_file="${2:-}"
      shift 2
      ;;
    --message-stdin)
      read_stdin="1"
      shift
      ;;
    --visual-confirmed)
      visual_confirmed="1"
      shift
      ;;
    --activate-lark)
      activate_lark="1"
      shift
      ;;
    --validate-only)
      mode="validate-only"
      shift
      ;;
    --paste-only)
      mode="paste-only"
      shift
      ;;
    --clear-only)
      mode="clear-only"
      shift
      ;;
    --send)
      mode="send"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 64
      ;;
  esac
done

if [[ -z "$expected_chat" ]]; then
  echo "Missing --expected-chat" >&2
  exit 64
fi

message=""
if [[ "$mode" != "validate-only" && "$mode" != "clear-only" ]]; then
  if [[ "$read_stdin" == "1" ]]; then
    message="$(cat)"
  elif [[ -n "$message_file" ]]; then
    message="$(cat "$message_file")"
  else
    echo "Paste/send mode requires --message-file or --message-stdin" >&2
    exit 64
  fi

  if [[ -z "${message//[$'\t\r\n ']/}" ]]; then
    echo "Refusing to paste/send an empty message" >&2
    exit 64
  fi

  printf '%s' "$message" | env -u LC_ALL LANG=en_US.UTF-8 LC_CTYPE=en_US.UTF-8 /usr/bin/pbcopy
fi

if [[ "$mode" != "validate-only" ]]; then
  bounds="$(
    /usr/bin/osascript - "$expected_chat" "$visual_confirmed" "$activate_lark" <<'APPLESCRIPT'
on run argv
  set expectedChat to item 1 of argv
  set visualConfirmed to item 2 of argv
  set activateLark to item 3 of argv

  tell application "System Events"
    if activateLark is "1" then
      try
        tell application id "com.electron.lark" to activate
      on error
        try
          tell application "Lark" to activate
        end try
      end try
      delay 0.5
    end if

    set frontProc to first application process whose frontmost is true
    set frontName to name of frontProc
    if frontName is not "Feishu" and frontName is not "Lark" and frontName is not "fei shu" and frontName is not "飞书" then
      error "Foreground app is not Feishu/Lark: " & frontName
    end if

    if not (exists front window of frontProc) then
      error "Feishu/Lark has no foreground window"
    end if

    set win to front window of frontProc
    set foundChat to false

    try
      set allItems to entire contents of win
      repeat with itemRef in allItems
        try
          set itemName to name of itemRef as text
          if itemName contains expectedChat then set foundChat to true
        end try
        try
          set itemValue to value of itemRef as text
          if itemValue contains expectedChat then set foundChat to true
        end try
        try
          set itemDesc to description of itemRef as text
          if itemDesc contains expectedChat then set foundChat to true
        end try
      end repeat
    on error errMsg
      error "Could not inspect Feishu UI. Check macOS Accessibility permission. " & errMsg
    end try

    if foundChat is false and visualConfirmed is not "1" then
      error "Visible Feishu chat does not contain expected Hermes bot name: " & expectedChat
    end if

    set winPos to position of win
    set winSize to size of win
    return (item 1 of winPos as text) & "," & (item 2 of winPos as text) & "," & (item 1 of winSize as text) & "," & (item 2 of winSize as text)
  end tell
end run
APPLESCRIPT
  )"

  IFS=',' read -r win_x win_y win_w win_h <<<"$bounds"

  click_point() {
    local x="$1"
    local y="$2"
    python3 - "$x" "$y" <<'PY'
import ctypes
import sys
import time

class CGPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

x = float(sys.argv[1])
y = float(sys.argv[2])
app = ctypes.CDLL('/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
app.CGWarpMouseCursorPosition.argtypes = [CGPoint]
app.CGEventCreateMouseEvent.restype = ctypes.c_void_p
app.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
app.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
app.CFRelease.argtypes = [ctypes.c_void_p]

pt = CGPoint(x, y)
app.CGWarpMouseCursorPosition(pt)
time.sleep(0.1)
for event_type in (1, 2):
    ev = app.CGEventCreateMouseEvent(None, event_type, pt, 0)
    app.CGEventPost(0, ev)
    app.CFRelease(ev)
    time.sleep(0.08)
PY
  }

  composer_x="$(python3 - "$win_x" "$win_w" <<'PY'
import sys
print(float(sys.argv[1]) + (float(sys.argv[2]) / 2))
PY
)"
  composer_y="$(python3 - "$win_y" "$win_h" <<'PY'
import sys
print(float(sys.argv[1]) + float(sys.argv[2]) - 46)
PY
)"

  click_point "$composer_x" "$composer_y"
  /usr/bin/osascript -e 'tell application "System Events" to keystroke "a" using command down'
  sleep 0.1

  if [[ "$mode" == "clear-only" ]]; then
    /usr/bin/osascript -e 'tell application "System Events" to key code 51'
    echo "CLEARED $expected_chat"
    exit 0
  fi

  /usr/bin/osascript -e 'tell application "System Events" to keystroke "v" using command down'
  sleep 0.4

  if [[ "$mode" == "paste-only" ]]; then
    echo "PASTED $expected_chat"
    exit 0
  fi

  if [[ "$mode" == "send" ]]; then
    send_x="$(python3 - "$win_x" "$win_w" <<'PY'
import sys
print(float(sys.argv[1]) + float(sys.argv[2]) - 74)
PY
)"
    send_y="$(python3 - "$win_y" "$win_h" <<'PY'
import sys
print(float(sys.argv[1]) + float(sys.argv[2]) - 46)
PY
)"
    click_point "$send_x" "$send_y"
    echo "SENT $expected_chat"
    exit 0
  fi

  echo "Unknown mode: $mode" >&2
  exit 64
fi

/usr/bin/osascript - "$expected_chat" "$mode" "$visual_confirmed" "$activate_lark" <<'APPLESCRIPT'
on run argv
  set expectedChat to item 1 of argv
  set modeName to item 2 of argv
  set visualConfirmed to item 3 of argv
  set activateLark to item 4 of argv

  tell application "System Events"
    if activateLark is "1" then
      try
        tell application id "com.electron.lark" to activate
      on error
        try
          tell application "Lark" to activate
        end try
      end try
      delay 0.5
    end if

    set frontProc to first application process whose frontmost is true
    set frontName to name of frontProc
    if frontName is not "Feishu" and frontName is not "Lark" and frontName is not "飞书" then
      error "Foreground app is not Feishu/Lark: " & frontName
    end if

    if not (exists front window of frontProc) then
      error "Feishu/Lark has no foreground window"
    end if

    set win to front window of frontProc
    set foundChat to false
    set scannedText to ""

    try
      set allItems to entire contents of win
      repeat with itemRef in allItems
        try
          set itemName to name of itemRef as text
          if itemName contains expectedChat then set foundChat to true
          if itemName is not "" then set scannedText to scannedText & " " & itemName
        end try
        try
          set itemValue to value of itemRef as text
          if itemValue contains expectedChat then set foundChat to true
          if itemValue is not "" then set scannedText to scannedText & " " & itemValue
        end try
        try
          set itemDesc to description of itemRef as text
          if itemDesc contains expectedChat then set foundChat to true
        end try
      end repeat
    on error errMsg
      error "Could not inspect Feishu UI. Check macOS Accessibility permission for Codex/Terminal/System Events. " & errMsg
    end try

    if foundChat is false and visualConfirmed is not "1" then
      error "Visible Feishu chat does not contain expected Hermes bot name: " & expectedChat
    end if

    if modeName is "validate-only" then
      return "VALIDATED " & expectedChat
    end if

    set winPos to position of win
    set winSize to size of win
    set winX to item 1 of winPos
    set winY to item 2 of winPos
    set winW to item 1 of winSize
    set winH to item 2 of winSize

    try
      click at {winX + (winW / 2), winY + winH - 46}
      delay 0.2
      keystroke "a" using command down
      delay 0.1
      if modeName is "clear-only" then
        key code 51
        delay 0.2
        return "CLEARED " & expectedChat
      end if
      keystroke "v" using command down
      delay 0.4
    on error errMsg
      error "GUI paste failed. Grant Accessibility to /usr/bin/osascript in System Settings -> Privacy & Security -> Accessibility. Original error: " & errMsg
    end try

    if modeName is "paste-only" then
      return "PASTED " & expectedChat
    end if

    if modeName is "send" then
      try
        click at {winX + winW - 42, winY + winH - 46}
        delay 0.3
      on error errMsg
        error "GUI send failed. Grant Accessibility to /usr/bin/osascript in System Settings -> Privacy & Security -> Accessibility. Original error: " & errMsg
      end try
      return "SENT " & expectedChat
    end if

    error "Unknown mode: " & modeName
  end tell
end run
APPLESCRIPT
