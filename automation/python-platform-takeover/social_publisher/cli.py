from __future__ import annotations

import os
from pathlib import Path

import typer

from social_publisher.browser import BrowserController, BrowserSessionConfig
from social_publisher.content_package import load_package
from social_publisher.platforms.base import pick_takeover_candidate
from social_publisher.platforms import build_publisher

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
        typer.echo(f"status: failed")
        typer.echo(f"ok: False")
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


def main() -> None:
    app()


def _safe_page_title(page: object) -> str:
    try:
        title = page.title()  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return "<unknown>"
    return title or "<untitled>"
