---
name: obsidian-knowledge-readback
description: "Read relevant content from the configured remote Obsidian Vault before answering questions that depend on project history, decisions, deployment, devices, business rules, or prior confirmed context."
---

# Obsidian 知识库回读

Use this skill when the answer may depend on the user's remote Obsidian knowledge base. It is a read-only skill: it does not create, edit, delete, rename, or sync notes.

## Decide whether to read

Perform a readback when any of the following is true:

- The user mentions Obsidian, Vault, knowledge base, prior notes, or asks to check records.
- The answer depends on historical decisions, deployment or device state, business rules, project conventions, confirmed preferences, or previous conclusions.
- The request is ambiguous and the Vault may resolve the ambiguity.
- The user explicitly says “先查 Obsidian” or equivalent.

For unrelated arithmetic, translation, general knowledge, creative writing, or code work with no dependency on project history, content readback may be skipped. If the user explicitly requests readback, never skip it.

## Required readback flow

1. Choose two to six distinctive search terms from the user's request. Do not use secrets, passwords, tokens, cookies, or private personal data as search terms.
2. Run the bundled read-only helper:

   macOS/Linux:

   ```bash
   bash scripts/obsidian-preflight.sh --query "<keywords>"
   ```

   Windows PowerShell:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\obsidian-preflight.ps1 -Query "<keywords>"
   ```

   Use `--manifest` on macOS/Linux or `-Manifest` on Windows when only the Vault file list and modification times are needed.
3. From the returned relative paths, select only a small number of relevant Markdown files. Read those files over SSH from the configured Vault; never read `.obsidian`, hidden directories, credentials, cookies, keys, tokens, complete environment files, private data, or unrelated large files.
4. Separate Vault evidence from inference. State when the Vault contains no supporting evidence. Do not present a remembered or guessed fact as verified.
5. Include the actual Obsidian relative path(s) used as sources in the answer. If the SSH connection or readback fails, report the failure and uncertainty before answering; do not fabricate a result.

## Connection context

- Remote host: `192.168.1.10:22`
- Vault: `/vol1/1000/Obsidian/obsidian-vault`
- macOS/Linux SSH key: `~/.ssh/id_ed25519_obsidian_bridge`
- Windows SSH key: `$HOME\.ssh\id_ed25519_obsidian_bridge`
- The remote bridge indexes Markdown separately; an index hit is not a substitute for reading the relevant source note when the user asks for verification.

The Vault path is intentionally a Linux path because the Vault is remote. Only the local SSH-key path changes between macOS/Linux and Windows.

## Write boundary

Do not write to the Vault from this skill or from an ordinary thread. Route confirmed knowledge that needs persistence to the dedicated “Obsidian 知识库更新与维护” thread. That thread alone may write under `Codex/Inbox/`, `Codex/Decisions/`, or `Codex/Runbooks/` under its existing safeguards.
