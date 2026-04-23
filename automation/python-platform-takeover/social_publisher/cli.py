from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone

import typer

from social_publisher.browser import BrowserController, BrowserSessionConfig
from social_publisher.content_package import load_package
from social_publisher.doctor import format_doctor_report, run_doctor
from social_publisher.env import load_dotenv_if_present
from social_publisher.platforms.base import pick_takeover_candidate
from social_publisher.platforms import build_publisher
from social_publisher.publish_receipts import (
    clear_receipt,
    get_receipt,
    PublishReceipt,
    receipt_path_for,
    should_block_republish,
    upsert_receipt,
)

app = typer.Typer(help="Multi-platform browser takeover scaffold.")


@app.command("validate-package")
def validate_package(package: Path) -> None:
    content_package = load_package(package)
    typer.echo(f"campaign_id: {content_package.campaign_id}")
    typer.echo(f"theme: {content_package.theme}")
    typer.echo("platforms:")
    for platform_id in sorted(content_package.platforms):
        typer.echo(f"- {platform_id}")


@app.command("readiness")
def readiness(platform: str) -> None:
    publisher = build_publisher(platform)
    typer.echo("\n".join(publisher.readiness_lines()))


@app.command("doctor")
def doctor(
    package: Path | None = typer.Option(
        None,
        "--package",
        help="Validate a content package and asset paths.",
    ),
    platform: str = typer.Option(
        "",
        "--platform",
        help="Validate a specific platform entry inside the package.",
    ),
    check_browser: bool = typer.Option(
        False,
        "--check-browser",
        help="Try connecting to the current CDP browser session.",
    ),
) -> None:
    report = run_doctor(
        package_path=package,
        platform_id=platform or None,
        check_browser=check_browser,
    )
    typer.echo("\n".join(format_doctor_report(report)))
    if report.has_failures:
        raise typer.Exit(1)


@app.command("inspect-tabs")
def inspect_tabs(
    url_contains: str = "",
    platform: str = typer.Option(
        "",
        "--platform",
        help="Inspect takeover candidates for a specific platform.",
    ),
    package: Path | None = typer.Option(
        None,
        "--package",
        help="Content package used to score existing draft tabs.",
    ),
) -> None:
    config = BrowserSessionConfig(cdp_url=os.getenv("BROWSER_CDP_URL"))
    with BrowserController(config) as controller:
        if platform:
            if package is None:
                raise typer.BadParameter("--package is required when --platform is set.")
            content_package = load_package(package)
            if platform not in content_package.platforms:
                raise typer.BadParameter(f"{platform} not found in package.")
            publisher = build_publisher(platform)
            candidates = publisher.inspect_takeover_candidates(
                controller,
                content_package.platforms[platform],
            )
            selected = pick_takeover_candidate(candidates)
            if candidates:
                ordered = sorted(
                    candidates,
                    key=lambda candidate: (
                        not candidate.stop_reasons,
                        candidate.score,
                        len(candidate.matched_fields),
                    ),
                    reverse=True,
                )
                for candidate in ordered:
                    if url_contains and url_contains not in candidate.page.url:
                        continue
                    prefix = "*" if candidate is selected else "-"
                    typer.echo(
                        f"{prefix} score={candidate.score} "
                        f"title={_safe_page_title(candidate.page)} "
                        f"url={candidate.page.url}"
                    )
                    if candidate.matched_fields:
                        typer.echo(
                            "  matched_fields: " + ", ".join(candidate.matched_fields)
                        )
                    if candidate.stop_reasons:
                        typer.echo(
                            "  stop_reasons: " + " | ".join(candidate.stop_reasons)
                        )
                    if candidate.notes:
                        typer.echo("  notes: " + " | ".join(candidate.notes))
                return
        matches = list(controller.describe_pages())
        for title, url in matches:
            if url_contains and url_contains not in url:
                continue
            typer.echo(f"- {title} :: {url}")


@app.command("publish")
def publish(
    platform: str,
    package: Path,
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Run the live publish flow when the platform implementation supports it.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Bypass the local publish receipt guard. Use only after the old item is removed or abandoned.",
    ),
) -> None:
    publisher = build_publisher(platform)
    content_package = load_package(package)
    if platform not in content_package.platforms:
        raise typer.BadParameter(f"{platform} not found in package.")

    if not execute:
        typer.echo(f"campaign_id: {content_package.campaign_id}")
        typer.echo(f"platform: {platform}")
        typer.echo("当前默认还是安全模式，先输出 readiness 清单。")
        typer.echo("")
        typer.echo("\n".join(publisher.readiness_lines()))
        typer.echo("")
        typer.echo("如果要真正执行，追加 --execute。")
        return

    existing_receipt = get_receipt(package, content_package.campaign_id, platform)
    if should_block_republish(existing_receipt) and not force:
        typer.echo("status: stopped_receipt_duplicate")
        typer.echo("ok: False")
        typer.echo("message: 本地发布台账已记录该 campaign/platform 已成功提交，停止重复发布。")
        typer.echo(f"receipt_path: {receipt_path_for(package, content_package.campaign_id)}")
        typer.echo(f"recorded_at: {existing_receipt.recorded_at}")
        typer.echo(f"receipt_status: {existing_receipt.status}")
        typer.echo(f"title: {existing_receipt.title}")
        if existing_receipt.current_url:
            typer.echo(f"current_url: {existing_receipt.current_url}")
        if existing_receipt.management_url:
            typer.echo(f"management_url: {existing_receipt.management_url}")
        return

    config = BrowserSessionConfig(cdp_url=os.getenv("BROWSER_CDP_URL"))
    try:
        with BrowserController(config) as controller:
            result = publisher.publish(
                controller,
                content_package.platforms[platform],
                content_package.assets,
                dry_run=False,
            )
    except Exception as exc:  # noqa: BLE001
        typer.echo("status: failed")
        typer.echo("ok: False")
        typer.echo(f"message: {exc}")
        raise typer.Exit(1) from exc
    typer.echo(f"status: {result.status}")
    typer.echo(f"ok: {result.ok}")
    typer.echo(f"message: {result.message}")
    if result.current_url:
        typer.echo(f"current_url: {result.current_url}")
    if result.management_url:
        typer.echo(f"management_url: {result.management_url}")
    if result.notes:
        typer.echo("notes:")
        for note in result.notes:
            typer.echo(f"- {note}")
    if result.ok and result.status.strip().lower() in {
        "submitted",
        "published",
        "under_review",
        "success",
        "verified",
    }:
        receipt = PublishReceipt(
            campaign_id=content_package.campaign_id,
            platform_id=platform,
            title=content_package.platforms[platform].title,
            status=result.status.strip().lower(),
            recorded_at=datetime.now(timezone.utc).isoformat(),
            current_url=result.current_url,
            management_url=result.management_url,
            notes=result.notes,
        )
        receipt_path = upsert_receipt(package, receipt)
        typer.echo(f"receipt_path: {receipt_path}")


@app.command("receipt-status")
def receipt_status(
    package: Path,
    platform: str = typer.Option(
        ...,
        "--platform",
        help="Inspect the local publish receipt for one platform.",
    ),
) -> None:
    content_package = load_package(package)
    receipt = get_receipt(package, content_package.campaign_id, platform)
    if receipt is None:
        typer.echo("status: missing")
        typer.echo("ok: False")
        return
    typer.echo("status: found")
    typer.echo("ok: True")
    typer.echo(f"receipt_path: {receipt_path_for(package, content_package.campaign_id)}")
    typer.echo(f"platform: {receipt.platform_id}")
    typer.echo(f"title: {receipt.title}")
    typer.echo(f"receipt_status: {receipt.status}")
    typer.echo(f"recorded_at: {receipt.recorded_at}")
    if receipt.current_url:
        typer.echo(f"current_url: {receipt.current_url}")
    if receipt.management_url:
        typer.echo(f"management_url: {receipt.management_url}")
    if receipt.external_id:
        typer.echo(f"external_id: {receipt.external_id}")
    if receipt.share_link:
        typer.echo(f"share_link: {receipt.share_link}")
    if receipt.notes:
        typer.echo("notes:")
        for note in receipt.notes:
            typer.echo(f"- {note}")


@app.command("record-receipt")
def record_receipt(
    package: Path,
    platform: str = typer.Option(
        ...,
        "--platform",
        help="Platform id to record.",
    ),
    status: str = typer.Option(
        ...,
        "--status",
        help="Receipt status such as submitted/published/under_review.",
    ),
    current_url: str = typer.Option("", "--current-url"),
    management_url: str = typer.Option("", "--management-url"),
    external_id: str = typer.Option("", "--external-id"),
    share_link: str = typer.Option("", "--share-link"),
) -> None:
    content_package = load_package(package)
    if platform not in content_package.platforms:
        raise typer.BadParameter(f"{platform} not found in package.")
    receipt = PublishReceipt(
        campaign_id=content_package.campaign_id,
        platform_id=platform,
        title=content_package.platforms[platform].title,
        status=status.strip().lower(),
        recorded_at=datetime.now(timezone.utc).isoformat(),
        current_url=current_url or None,
        management_url=management_url or None,
        external_id=external_id or None,
        share_link=share_link or None,
    )
    receipt_path = upsert_receipt(package, receipt)
    typer.echo("status: recorded")
    typer.echo("ok: True")
    typer.echo(f"receipt_path: {receipt_path}")


@app.command("clear-receipt")
def clear_receipt_command(
    package: Path,
    platform: str = typer.Option(
        ...,
        "--platform",
        help="Platform id to clear from the local publish receipt ledger.",
    ),
) -> None:
    content_package = load_package(package)
    removed = clear_receipt(package, content_package.campaign_id, platform)
    typer.echo(f"status: {'cleared' if removed else 'missing'}")
    typer.echo(f"ok: {removed}")


def main() -> None:
    load_dotenv_if_present()
    app()


def _safe_page_title(page: object) -> str:
    try:
        title = page.title()  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return "<unknown>"
    return title or "<untitled>"
