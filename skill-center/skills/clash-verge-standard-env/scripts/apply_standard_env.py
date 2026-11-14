#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG_DIR = Path.home() / "Library/Application Support/io.github.clash-verge-rev.clash-verge-rev"
SKILL_DIR = Path(__file__).resolve().parent.parent
VERGE_TEMPLATE = SKILL_DIR / "references/verge.template.yaml"
RULES_TEMPLATE = SKILL_DIR / "references/rules-enhancement.yaml"
FALLBACK_RULES_FILE = "clash-verge-standard-rules.yaml"


def replace_first(pattern: str, repl: str, text: str) -> tuple[str, bool]:
    new_text, count = re.subn(pattern, repl, text, count=1, flags=re.M)
    return new_text, count > 0


def copy_template(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def patch_profiles_yaml(text: str, interval: int) -> tuple[str, str | None]:
    text, _ = replace_first(r"(^\s+update_interval:\s*)\d+", rf"\g<1>{interval}", text)
    text, _ = replace_first(r"(^\s+allow_auto_update:\s*)\w+", r"\g<1>true", text)
    rules_match = re.search(r"^\s+rules:\s*([A-Za-z0-9_-]+)\s*$", text, flags=re.M)
    return text, rules_match.group(1) if rules_match else None


def reload_running_config(config_dir: Path) -> bool:
    sock = Path("/tmp/verge/verge-mihomo.sock")
    config_path = config_dir / "clash-verge.yaml"
    if not sock.exists() or not config_path.exists():
        return False
    cmd = [
        "curl",
        "--unix-socket",
        str(sock),
        "-s",
        "-X",
        "PUT",
        "-H",
        "Content-Type: application/json",
        "-d",
        f'{{"path":"{config_path}"}}',
        "http://localhost/configs",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the standard Clash Verge environment.")
    parser.add_argument("--config-dir", default=str(DEFAULT_CONFIG_DIR))
    parser.add_argument("--update-interval", type=int, default=1440)
    args = parser.parse_args()

    config_dir = Path(args.config_dir).expanduser()
    if not config_dir.exists():
        print(f"Config directory not found: {config_dir}", file=sys.stderr)
        print("Install and launch Clash Verge once before running this script.", file=sys.stderr)
        return 1

    verge_path = config_dir / "verge.yaml"
    profiles_dir = config_dir / "profiles"
    profiles_yaml = config_dir / "profiles.yaml"

    copy_template(VERGE_TEMPLATE, verge_path)
    print(f"Applied standard preferences to: {verge_path}")

    rules_output: Path
    if profiles_yaml.exists():
        text = profiles_yaml.read_text(encoding="utf-8")
        patched_text, rules_uid = patch_profiles_yaml(text, args.update_interval)
        profiles_yaml.write_text(patched_text, encoding="utf-8")
        rules_output = profiles_dir / f"{rules_uid}.yaml" if rules_uid else profiles_dir / FALLBACK_RULES_FILE
        print(f"Updated remote profile auto-update interval to {args.update_interval} minutes.")
    else:
        rules_output = profiles_dir / FALLBACK_RULES_FILE
        print("profiles.yaml not found; skipped remote profile patching.")

    copy_template(RULES_TEMPLATE, rules_output)
    print(f"Applied standard enhancement rules to: {rules_output}")

    if reload_running_config(config_dir):
        print("Reloaded the running Clash Verge core config.")
    else:
        print("Clash Verge core was not reloaded automatically. Open Clash Verge and refresh if needed.")

    if not profiles_yaml.exists():
        print("Import a subscription in Clash Verge, then rerun this script so the remote profile picks up the standard rules file.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
