from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_platform_mapping(platform_id: str) -> dict[str, Any]:
    mapping_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "platform-mappings"
        / f"{platform_id}.yaml"
    )
    if not mapping_path.exists():
        raise FileNotFoundError(f"Missing platform mapping: {mapping_path}")
    payload = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid platform mapping: {mapping_path}")
    return payload
