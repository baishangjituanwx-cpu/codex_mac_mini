from __future__ import annotations

from dataclasses import dataclass, field
import platform as platform_runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from social_publisher.browser import BrowserController
    from social_publisher.content_package import AssetPaths, PlatformContent
    from playwright.sync_api import Locator


@dataclass(frozen=True)
class PlatformMetadata:
    platform_id: str
    display_name: str
    compose_urls: list[str]
    management_urls: list[str]
    prechecks: list[str]
    manual_checkpoints: list[str]
    success_signals: list[str]
    takeover_allowed: list[str]
    takeover_stop_conditions: list[str]


@dataclass
class PublishResult:
    ok: bool
    status: str
    message: str
    current_url: str | None = None
    management_url: str | None = None
    notes: list[str] = field(default_factory=list)


class PlatformPublisher:
    metadata: PlatformMetadata

    def readiness_lines(self) -> list[str]:
        lines: list[str] = []
        lines.append(f"平台: {self.metadata.display_name}")
        lines.append("发布入口:")
        lines.extend(f"- {url}" for url in self.metadata.compose_urls)
        lines.append("管理页:")
        lines.extend(f"- {url}" for url in self.metadata.management_urls)
        lines.append("接管前检查:")
        lines.extend(f"- {item}" for item in self.metadata.prechecks)
        lines.append("人工检查点:")
        lines.extend(f"- {item}" for item in self.metadata.manual_checkpoints)
        lines.append("成功信号:")
        lines.extend(f"- {item}" for item in self.metadata.success_signals)
        lines.append("允许直接接管的页面:")
        lines.extend(f"- {item}" for item in self.metadata.takeover_allowed)
        lines.append("必须停止的条件:")
        lines.extend(f"- {item}" for item in self.metadata.takeover_stop_conditions)
        return lines

    def publish(
        self,
        controller: "BrowserController",
        platform_content: "PlatformContent",
        assets: "AssetPaths",
        *,
        dry_run: bool = False,
    ) -> PublishResult:
        raise NotImplementedError(
            f"{self.metadata.display_name} publish flow is not implemented yet."
        )


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def content_snippet(value: str, *, limit: int = 18) -> str:
    normalized = normalize_text(value)
    return normalized[:limit]


def primary_select_all_shortcut() -> str:
    return "Meta+A" if platform_runtime.system() == "Darwin" else "Control+A"


def read_locator_text(locator: "Locator | None") -> str:
    if locator is None:
        return ""
    try:
        value = locator.input_value(timeout=1500)
    except Exception:  # noqa: BLE001
        try:
            value = locator.inner_text(timeout=1500)
        except Exception:  # noqa: BLE001
            return ""
    return normalize_text(value)


def text_matches_target(current: str, target: str) -> bool:
    normalized_current = normalize_text(current)
    normalized_target = normalize_text(target)
    if not normalized_current or not normalized_target:
        return True
    return (
        normalized_current in normalized_target
        or normalized_target in normalized_current
    )


def detect_text_mismatch(
    field_name: str,
    current: str,
    target: str,
    *,
    limit: int = 80,
) -> str | None:
    normalized_current = normalize_text(current)
    if not normalized_current:
        return None
    if text_matches_target(normalized_current, target):
        return None
    return f"existing_{field_name}: {normalized_current[:limit]}"
