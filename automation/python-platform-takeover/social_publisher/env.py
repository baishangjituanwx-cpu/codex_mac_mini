from __future__ import annotations

import os
from pathlib import Path


def load_dotenv_if_present() -> Path | None:
    for path in candidate_env_paths():
        if not path.is_file():
            continue
        _apply_env_file(path)
        return path
    return None


def candidate_env_paths() -> list[Path]:
    cwd_env = Path.cwd() / ".env"
    project_env = project_root() / ".env"
    candidates = [cwd_env]
    if project_env != cwd_env:
        candidates.append(project_env)
    return candidates


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _apply_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, separator, value = line.partition("=")
        if not separator:
            continue
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
