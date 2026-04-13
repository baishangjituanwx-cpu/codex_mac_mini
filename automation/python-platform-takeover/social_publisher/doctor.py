from __future__ import annotations

import importlib.util
import os
import platform
from dataclasses import dataclass
from pathlib import Path

from social_publisher.browser import BrowserController, BrowserSessionConfig
from social_publisher.content_package import ContentPackage, PlatformContent, load_package
from social_publisher.env import candidate_env_paths, project_root
from social_publisher.platforms import build_publisher

PLACEHOLDER_MARKERS = (
    "/ABS/PATH/",
    "C:/ABS/PATH/",
    "{{WORKSPACE_ROOT}}",
    "<replace",
    "<todo",
)


@dataclass
class DoctorCheck:
    status: str
    name: str
    message: str


@dataclass
class DoctorReport:
    checks: list[DoctorCheck]
    package_path: Path | None = None

    @property
    def has_failures(self) -> bool:
        return any(check.status == "fail" for check in self.checks)


def run_doctor(
    *,
    package_path: Path | None = None,
    platform_id: str | None = None,
    check_browser: bool = False,
) -> DoctorReport:
    checks: list[DoctorCheck] = []
    checks.append(
        DoctorCheck(
            status="ok",
            name="python",
            message=f"{platform.python_implementation()} {platform.python_version()}",
        )
    )
    checks.extend(_dependency_checks())
    checks.append(_env_file_check())

    cdp_url = os.getenv("BROWSER_CDP_URL", "").strip()
    if cdp_url:
        checks.append(DoctorCheck("ok", "BROWSER_CDP_URL", cdp_url))
    else:
        checks.append(
            DoctorCheck(
                "fail" if check_browser else "warn",
                "BROWSER_CDP_URL",
                "未设置；真实接管现有标签页时需要它。",
            )
        )

    takeover_mode = os.getenv("DEFAULT_TAKEOVER_MODE", "").strip()
    if takeover_mode == "existing-tab":
        checks.append(DoctorCheck("ok", "DEFAULT_TAKEOVER_MODE", takeover_mode))
    elif takeover_mode:
        checks.append(
            DoctorCheck(
                "warn",
                "DEFAULT_TAKEOVER_MODE",
                f"{takeover_mode}；当前推荐使用 existing-tab。",
            )
        )
    else:
        checks.append(
            DoctorCheck("warn", "DEFAULT_TAKEOVER_MODE", "未设置；推荐 existing-tab。")
        )

    resolved_package = _resolve_default_package(package_path)
    content_package: ContentPackage | None = None
    if resolved_package is not None:
        try:
            content_package = load_package(resolved_package)
        except Exception as exc:  # noqa: BLE001
            checks.append(
                DoctorCheck(
                    "fail",
                    "content_package",
                    f"{resolved_package}: {exc}",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    "ok",
                    "content_package",
                    f"{resolved_package} ({content_package.campaign_id})",
                )
            )
            checks.extend(_package_checks(content_package, resolved_package, platform_id))
    else:
        checks.append(
            DoctorCheck(
                "warn",
                "content_package",
                "未提供 --package，且默认的 configs/content-package.local.yaml 不存在。",
            )
        )

    if check_browser:
        checks.append(_browser_check(cdp_url))

    return DoctorReport(checks=checks, package_path=resolved_package)


def format_doctor_report(report: DoctorReport) -> list[str]:
    lines = [
        f"status: {'ok' if not report.has_failures else 'needs_attention'}",
    ]
    if report.package_path is not None:
        lines.append(f"package: {report.package_path}")
    for check in report.checks:
        lines.append(f"{check.status.upper():<4} {check.name}: {check.message}")
    return lines


def _dependency_checks() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    for module_name in ("yaml", "typer", "playwright"):
        if importlib.util.find_spec(module_name) is not None:
            checks.append(DoctorCheck("ok", f"dependency:{module_name}", "installed"))
        else:
            checks.append(
                DoctorCheck(
                    "fail",
                    f"dependency:{module_name}",
                    "未安装；先执行 quickstart 或 README 里的安装步骤。",
                )
            )
    return checks


def _env_file_check() -> DoctorCheck:
    for path in candidate_env_paths():
        if path.is_file():
            return DoctorCheck("ok", ".env", str(path))
    return DoctorCheck("warn", ".env", "未找到 .env；将只使用当前 shell 里的环境变量。")


def _resolve_default_package(package_path: Path | None) -> Path | None:
    if package_path is not None:
        return package_path.expanduser().resolve()
    default_package = project_root() / "configs" / "content-package.local.yaml"
    if default_package.is_file():
        return default_package
    return None


def _package_checks(
    content_package: ContentPackage,
    package_path: Path,
    platform_id: str | None,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    package_dir = package_path.parent

    if platform_id:
        try:
            build_publisher(platform_id)
        except KeyError:
            checks.append(
                DoctorCheck("fail", "platform", f"{platform_id} 不是已注册的平台。")
            )
        else:
            if platform_id not in content_package.platforms:
                checks.append(
                    DoctorCheck(
                        "fail",
                        "platform",
                        f"{platform_id} 不在当前内容包里。",
                    )
                )
            else:
                checks.append(DoctorCheck("ok", "platform", platform_id))
                checks.extend(
                    _platform_content_checks(
                        platform_id,
                        content_package.platforms[platform_id],
                    )
                )

    checks.extend(
        [
            _asset_check("assets.main_video", content_package.assets.main_video, package_dir, required=True),
            _asset_check("assets.backup_video", content_package.assets.backup_video, package_dir, required=False),
            _asset_check("assets.cover_3_4", content_package.assets.cover_3_4, package_dir, required=False),
            _asset_check("assets.cover_4_3", content_package.assets.cover_4_3, package_dir, required=False),
        ]
    )
    return checks


def _platform_content_checks(
    platform_id: str,
    content: PlatformContent,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    title = content.title.strip()
    description = content.description.strip()

    if title:
        checks.append(
            DoctorCheck(
                "ok",
                f"{platform_id}.title",
                f"{len(title)} chars",
            )
        )
    else:
        checks.append(
            DoctorCheck("fail", f"{platform_id}.title", "为空。")
        )

    if description:
        checks.append(
            DoctorCheck(
                "ok",
                f"{platform_id}.description",
                f"{len(description)} chars",
            )
        )
    else:
        checks.append(
            DoctorCheck("fail", f"{platform_id}.description", "为空。")
        )
    return checks


def _asset_check(
    label: str,
    raw_value: str | None,
    package_dir: Path,
    *,
    required: bool,
) -> DoctorCheck:
    if not raw_value:
        return DoctorCheck(
            "fail" if required else "warn",
            label,
            "未填写。",
        )

    value = raw_value.strip()
    lowered = value.lower()
    if any(marker.lower() in lowered for marker in PLACEHOLDER_MARKERS):
        return DoctorCheck("warn", label, f"仍是占位路径: {value}")

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (package_dir / path).resolve()
        if path.exists():
            return DoctorCheck("ok", label, f"{path} (relative)")
        return DoctorCheck("warn", label, f"相对路径不存在: {path}")

    if path.exists():
        return DoctorCheck("ok", label, str(path))
    return DoctorCheck("warn", label, f"路径不存在: {path}")


def _browser_check(cdp_url: str) -> DoctorCheck:
    if not cdp_url:
        return DoctorCheck("fail", "browser", "无法检查；BROWSER_CDP_URL 未设置。")

    try:
        with BrowserController(BrowserSessionConfig(cdp_url=cdp_url)) as controller:
            page_count = len(list(controller.describe_pages()))
    except Exception as exc:  # noqa: BLE001
        return DoctorCheck("fail", "browser", f"CDP 连接失败: {exc}")
    return DoctorCheck("ok", "browser", f"CDP 已连接，当前可见标签页 {page_count} 个。")
