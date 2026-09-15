---
name: obsidian-knowledge-capture
description: "Capture confirmed decisions, preferences, rules, and reusable project knowledge into the configured Obsidian Vault through the allowlisted Codex threads."
---

# Obsidian 即时知识沉淀

Use this skill when the user explicitly asks to immediately capture, persist, revise, or confirm knowledge in Obsidian, including the triggers `【立即沉淀】`, `【待确认沉淀】`, and `【修订 Obsidian】`.

## Modes

- `【立即沉淀】`: the user has confirmed the content. Extract only stable, explicit facts and route the write through the allowlisted thread that owns the current work.
- `【待确认沉淀】`: prepare a concise proposed note or capture packet in the current reply. Do not write to the Vault.
- `【修订 Obsidian】`: first read the relevant existing note, identify the exact change, then route the authorized revision to an allowlisted thread.

If the user uses ordinary wording such as “把本轮已确认内容立即沉淀到 Obsidian”, treat it as `【立即沉淀】`. If the content is ambiguous, contradictory, speculative, or still under discussion, do not write it; ask for confirmation or use the pending-confirmation mode.

## Capture workflow

1. Read the current conversation and separate confirmed facts, decisions, preferences, constraints, open questions, and proposed actions. Do not promote an inference or temporary status into a durable rule.
2. Run the configured read-only Obsidian preflight/search before writing. Read only a small number of relevant Markdown notes and cite their relative paths. If Vault access or SSH fails, stop and report the failure.
3. Build a compact, deduplicated capture packet. Prefer a meaningful title, project/scope, content type, confirmation date, source thread, and last-verified information. Do not copy the whole conversation.
4. Only these exact Codex thread IDs may perform the remote write: `01a08ac5-a2e1-7341-a4c0-8c0b481d50bc`, `01a09485-ace3-7422-875f-a267b1e4ceae`, `019f0326-58b0-78a0-928b-be7bac29a7c9`, `01a09a0f-c8c9-7b80-b637-bce085b18105`, and `01a0857a-5528-7e72-ab62-5aebdcf59b18`. All other threads are read-only.
5. The allowlisted thread must read the proposed target and related notes before writing, write only under `Codex/Inbox/`, `Codex/Decisions/`, or `Codex/Runbooks/`, and never overwrite, delete, or rename unrelated notes.
6. After writing, the allowlisted thread must read the exact target back through the same formal path, verify the title and key content, wait for `knowledge-bridge`, and report the relative path plus real synchronization evidence. HTTP success, a local draft, or an unverified API response is not sufficient.

## Placement guidance

- `Codex/Inbox/`: confirmed capture packets, operational run records, and items awaiting later consolidation.
- `Codex/Decisions/`: durable decisions, user preferences, business rules, and project commitments.
- `Codex/Runbooks/`: repeatable procedures, checklists, and troubleshooting flows.

## Safety boundaries

- Never write passwords, SSH credentials, private keys, Cookies, Tokens, complete environment variables, private personal data, or unrelated large content.
- Never treat “审核中”, a draft, an HTTP 200, an old snapshot, or a summary as final business evidence when the source workflow requires a fresh readback.
- Do not write outside the three permitted `Codex/` subdirectories.
- The allowlist is a policy-level control, not a platform-level ACL. Direct desktop threads may still bypass the skill; each writer must verify its own thread ID and use the validated Obsidian-Codex Gateway when deterministic “read first, then answer” ordering is required.

## User-facing completion format

For a successful immediate capture, report:

- capture mode and a one-sentence summary;
- the actual Obsidian relative path;
- whether a prior note was read and deduplicated;
- write/readback verification;
- bridge synchronization evidence.

If any required step fails, state the exact failed step and do not claim the knowledge was persisted.

## Windows Repo Mirror Notes

- Windows uses the same three capture modes, allowlisted-thread routing, write boundaries, and read-back requirements; there is no separate business or policy implementation.
- Before any authorized write, reuse the repository's `obsidian-knowledge-readback` PowerShell entry for the manifest, query, and restricted Markdown read. Keep the remote Linux Vault path `/vol1/1000/Obsidian/obsidian-vault` unchanged.
- Windows OpenSSH credentials stay in `%USERPROFILE%\\.ssh\\id_ed25519_obsidian_bridge`; do not put keys, tokens, or full environment values in command arguments, Task Scheduler fields, or local notes.
- The workflow is keyboard-free and needs no Mac-to-Windows shortcut remapping. No additional `.ps1` or `.cmd` mutation wrapper is required; writes remain limited to the allowlisted Codex thread and the three permitted remote subdirectories.
