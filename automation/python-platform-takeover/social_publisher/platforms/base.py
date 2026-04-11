from __future__ import annotations

from dataclasses import dataclass


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

    def publish(self) -> None:
        raise NotImplementedError(
            f"{self.metadata.display_name} publish flow is not implemented yet."
        )
