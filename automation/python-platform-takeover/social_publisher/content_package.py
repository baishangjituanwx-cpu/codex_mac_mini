from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AssetPaths:
    main_video: str
    backup_video: str | None = None
    cover_3_4: str | None = None
    cover_4_3: str | None = None


@dataclass
class PlatformContent:
    title: str
    description: str


@dataclass
class ContentPackage:
    campaign_id: str
    theme: str
    assets: AssetPaths
    platforms: dict[str, PlatformContent]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ContentPackage":
        assets = AssetPaths(**payload["assets"])
        platforms = {
            platform_id: PlatformContent(**platform_payload)
            for platform_id, platform_payload in payload["platforms"].items()
        }
        return cls(
            campaign_id=payload["campaign_id"],
            theme=payload["theme"],
            assets=assets,
            platforms=platforms,
        )


def load_package(path: str | Path) -> ContentPackage:
    package_path = Path(path)
    payload = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid content package: {package_path}")
    return ContentPackage.from_mapping(payload)
