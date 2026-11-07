---
name: clash-verge-standard-env
description: Use this skill to set up or sync a standard Clash Verge environment on a Mac so another device matches the same Clash Verge preferences as this machine, excluding the actual subscription URL. Use it when Codex should configure Clash Verge defaults, system proxy behavior, auto-update interval, built-in test items, and app-specific direct rules such as keeping the app "远程看看" off Clash.
---

# Clash Verge Standard Env

Use this skill when the user wants another Mac with `Codex + Clash Verge` to quickly match the same Clash Verge preference set used on this machine, without copying the private subscription URL.

## What This Skill Standardizes

- Clash Verge UI and behavior preferences from `verge.yaml`
- System proxy enabled by default
- Auto-launch and app behavior preferences
- Built-in latency test items
- Remote subscription auto-update interval
- Rule enhancement file content
- Direct-connect rules for:
  - `远程看看`
  - `aomeisoftware.com`
  - `anyviewer.com`

## What This Skill Does Not Copy

- The real subscription URL
- Runtime cache, generated logs, or old node history
- Temporary generated files that Clash Verge can rebuild

## Workflow

1. Confirm Clash Verge is installed on the target Mac.
2. Locate the config directory:
   - `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev`
3. Run:

```bash
python3 ~/.codex/skills/clash-verge-standard-env/scripts/apply_standard_env.py
```

4. If the target machine already has a remote subscription profile, the script will:
   - keep the existing subscription URL
   - set remote auto-update to `1440` minutes
   - overwrite the linked rules-enhancement file with the standard direct rules
5. If the target machine does not yet have a remote subscription profile, the script will still:
   - apply the standard `verge.yaml`
   - create a reusable rules template file
   - report that the user should import a subscription and rerun the script

## Notes

- Prefer rerunning the script over manual edits when syncing a new machine.
- Do not copy `clash-verge.yaml` or logs from one Mac to another as the primary migration path. Those are generated/runtime artifacts.
- After the script runs, if Clash Verge is active, it will try to reload the running config automatically.

## Resources

### scripts/

- `apply_standard_env.py`
  Applies the standard Clash Verge preferences and rules to the local Clash Verge config directory.

### references/

- `verge.template.yaml`
  Canonical Clash Verge preference template used for migration.
- `rules-enhancement.yaml`
  Canonical enhancement rules, including direct rules for `远程看看`.
