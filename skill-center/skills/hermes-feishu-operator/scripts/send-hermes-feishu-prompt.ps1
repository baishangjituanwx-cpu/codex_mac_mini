param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedChat = "hermes_agent_mac_mini"
$mode = "validate-only"
$messageFile = ""
$readStdin = $false
$visualConfirmed = $false
$activateLark = $false

function Show-Usage {
  @'
Usage:
  send-hermes-feishu-prompt.ps1 --expected-chat hermes_agent_mac_mini --validate-only
  send-hermes-feishu-prompt.ps1 --expected-chat hermes_agent_mac_mini --message-file C:/work/prompt.txt --paste-only
  Get-Content -Raw C:/work/prompt.txt | send-hermes-feishu-prompt.ps1 --expected-chat hermes_agent_mac_mini --message-stdin --send
  Get-Content -Raw C:/work/prompt.txt | send-hermes-feishu-prompt.ps1 --expected-chat hermes_agent_mac_mini --visual-confirmed --message-stdin --send

Modes:
  --validate-only    Verify Feishu/Lark is foreground and the visible chat title contains the expected chat name.
  --paste-only       Paste the message into the verified chat input, but do not send.
  --clear-only       Clear the verified chat input, but do not paste or send.
  --send             Paste the message, then press Enter in the verified chat.
  --visual-confirmed Permit paste/send when Codex has just visually confirmed the chat in a screenshot.
  --activate-lark    Bring Lark/Feishu to foreground before validating.
'@
}

for ($i = 0; $i -lt $RemainingArgs.Count; $i++) {
  switch ($RemainingArgs[$i]) {
    "--expected-chat" {
      if ($i + 1 -ge $RemainingArgs.Count) {
        throw "Missing value for --expected-chat"
      }
      $i++
      $expectedChat = $RemainingArgs[$i]
    }
    "--message-file" {
      if ($i + 1 -ge $RemainingArgs.Count) {
        throw "Missing value for --message-file"
      }
      $i++
      $messageFile = $RemainingArgs[$i]
    }
    "--message-stdin" {
      $readStdin = $true
    }
    "--visual-confirmed" {
      $visualConfirmed = $true
    }
    "--activate-lark" {
      $activateLark = $true
    }
    "--validate-only" {
      $mode = "validate-only"
    }
    "--paste-only" {
      $mode = "paste-only"
    }
    "--clear-only" {
      $mode = "clear-only"
    }
    "--send" {
      $mode = "send"
    }
    "-h" {
      Show-Usage
      exit 0
    }
    "--help" {
      Show-Usage
      exit 0
    }
    default {
      throw "Unknown argument: $($RemainingArgs[$i])"
    }
  }
}

if ([string]::IsNullOrWhiteSpace($expectedChat)) {
  throw "Missing --expected-chat"
}

if (-not ("HermesForegroundWindow" -as [type])) {
  Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class HermesForegroundWindow {
  [DllImport("user32.dll")]
  public static extern IntPtr GetForegroundWindow();

  [DllImport("user32.dll")]
  public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

  [DllImport("user32.dll", CharSet = CharSet.Unicode)]
  public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@
}

function Get-FeishuCandidateProcesses {
  $names = @("Lark", "Feishu")
  $processes = foreach ($name in $names) {
    Get-Process -Name $name -ErrorAction SilentlyContinue |
      Where-Object { $_.MainWindowHandle -ne 0 }
  }
  $processes | Sort-Object StartTime
}

function Get-ForegroundWindowInfo {
  $handle = [HermesForegroundWindow]::GetForegroundWindow()
  if ($handle -eq [IntPtr]::Zero) {
    throw "Could not determine the foreground window."
  }

  $processId = 0
  [void][HermesForegroundWindow]::GetWindowThreadProcessId($handle, [ref]$processId)
  if (-not $processId) {
    throw "Could not determine the foreground process."
  }

  $process = Get-Process -Id $processId
  $builder = New-Object System.Text.StringBuilder 1024
  [void][HermesForegroundWindow]::GetWindowText($handle, $builder, $builder.Capacity)

  [pscustomobject]@{
    Handle = $handle
    Process = $process
    Title = $builder.ToString()
  }
}

function Activate-LarkWindow {
  $target = Get-FeishuCandidateProcesses | Select-Object -First 1
  if (-not $target) {
    throw "Could not find a visible Feishu/Lark window to activate."
  }

  $shell = New-Object -ComObject WScript.Shell
  if (-not $shell.AppActivate([int]$target.Id)) {
    throw "Failed to activate Feishu/Lark."
  }
  Start-Sleep -Milliseconds 500
}

function Set-ClipboardText {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Text
  )

  if (Get-Command Set-Clipboard -ErrorAction SilentlyContinue) {
    Set-Clipboard -Value $Text
    return
  }

  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.Clipboard]::SetText($Text)
}

function Send-KeySequence {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Keys,
    [int]$DelayMs = 180
  )

  $shell = New-Object -ComObject WScript.Shell
  [void]$shell.SendKeys($Keys)
  Start-Sleep -Milliseconds $DelayMs
}

function Test-ChatWindow {
  if ($activateLark) {
    Activate-LarkWindow
  }

  $front = Get-ForegroundWindowInfo
  $frontName = $front.Process.ProcessName
  $frontTitle = $front.Title
  $isLark = @("Lark", "Feishu") -contains $frontName

  if (-not $isLark) {
    throw "Foreground app is not Feishu/Lark: $frontName"
  }

  $chatVisible = $false
  if ($frontTitle) {
    $chatVisible = $frontTitle.IndexOf($expectedChat, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
  }

  if (-not $chatVisible -and -not $visualConfirmed) {
    throw "Foreground window title does not contain expected Hermes bot name: $expectedChat"
  }

  return $front
}

$message = ""
if ($mode -ne "validate-only" -and $mode -ne "clear-only") {
  if ($readStdin) {
    $message = [Console]::In.ReadToEnd()
  } elseif ($messageFile) {
    if (-not (Test-Path -LiteralPath $messageFile)) {
      throw "Message file not found: $messageFile"
    }
    $message = Get-Content -LiteralPath $messageFile -Raw
  } else {
    throw "Paste/send mode requires --message-file or --message-stdin"
  }

  if ([string]::IsNullOrWhiteSpace($message)) {
    throw "Refusing to paste/send an empty message"
  }

  Set-ClipboardText -Text $message
}

$front = Test-ChatWindow

if ($mode -eq "validate-only") {
  Write-Output "VALIDATED $expectedChat"
  exit 0
}

$shell = New-Object -ComObject WScript.Shell
if (-not $shell.AppActivate([int]$front.Process.Id)) {
  throw "Failed to focus the verified Feishu/Lark window."
}
Start-Sleep -Milliseconds 300

Send-KeySequence -Keys "^a"

if ($mode -eq "clear-only") {
  Send-KeySequence -Keys "{BACKSPACE}" -DelayMs 220
  Write-Output "CLEARED $expectedChat"
  exit 0
}

Send-KeySequence -Keys "{BACKSPACE}" -DelayMs 220
Send-KeySequence -Keys "^v" -DelayMs 450

if ($mode -eq "paste-only") {
  Write-Output "PASTED $expectedChat"
  exit 0
}

if ($mode -eq "send") {
  Send-KeySequence -Keys "{ENTER}" -DelayMs 250
  Write-Output "SENT $expectedChat"
  exit 0
}

throw "Unknown mode: $mode"
