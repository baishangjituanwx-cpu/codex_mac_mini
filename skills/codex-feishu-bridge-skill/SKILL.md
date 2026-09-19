---
name: "codex-feishu-bridge"
description: "Use when the user wants to install, deploy, operate, troubleshoot, or package a Feishu-to-Codex bridge that routes Feishu bot messages into local Codex threads, supports thread binding and resume, and mirrors chat history locally."
---

# Codex Feishu Bridge

This skill packages and operates a Feishu-to-Codex bridge built around:

- `@larksuite/cli` for Feishu auth, event subscription, and message send/reply
- local `codex` CLI for thread execution and resume
- a local Node bridge process for chat binding, thread state, and mirrored history

## Use this skill when

- the user wants to connect Feishu Bot to local Codex
- the user wants deployment instructions for another machine
- the user wants a reusable Codex skill/bundle for the bridge
- the user wants usage guidance for Feishu commands, mirrored history, or local mirror viewing
- the user wants to troubleshoot `lark-cli`, launchd, mirror files, or thread binding

## Workflow

1. Read [deployment.md](./references/deployment.md) for machine setup, prerequisites, and the recommended deployment path.
2. Read [user-guide.md](./references/user-guide.md) for operator-facing commands and normal usage flows.
3. Read [architecture.md](./references/architecture.md) if you need the bridge internals, file layout, or limits.
4. Use the bundled installer in [install_bridge_template.sh](./scripts/install_bridge_template.sh) on macOS, or [install_bridge_template.ps1](./scripts/install_bridge_template.ps1) on Windows, when deploying the template to another machine.
5. Use the bundled template under `assets/template/` as the source of truth for deployed bridge files.

## Deployment rules

- Default install target:
  - macOS: `~/.codex-feishu-bridge`
  - Windows: `%USERPROFILE%\.codex-feishu-bridge`
- Prefer user-scoped `launchd` under `~/Library/LaunchAgents` on macOS.
- Prefer the bundled per-user PowerShell launchers on Windows.
- Do not claim the deployed bridge is read-only unless a real permission or sandbox failure occurred
- Preserve user secrets locally; never store `App Secret` in shared docs or logs
- Keep Feishu usage to private bot chats unless the user explicitly wants group routing

## Template structure

- `assets/template/src/bridge.js`
- `assets/template/scripts/*.sh`
- `assets/template/scripts/*.ps1`
- `assets/template/scripts/*.cmd`
- `assets/template/scripts/*.command`
- `assets/template/launchd/com.codex.feishu-bridge.plist`
- `assets/template/package.json`

The installer rewrites `__INSTALL_DIR__` placeholders during deployment.
