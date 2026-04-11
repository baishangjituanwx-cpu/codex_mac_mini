from __future__ import annotations

import os
from pathlib import Path

import typer

from social_publisher.browser import BrowserController, BrowserSessionConfig
from social_publisher.content_package import load_package
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
def inspect_tabs(url_contains: str = "") -> None:
    config = BrowserSessionConfig(cdp_url=os.getenv("BROWSER_CDP_URL"))
    with BrowserController(config) as controller:
        matches = list(controller.describe_pages())
        for title, url in matches:
            if url_contains and url_contains not in url:
                continue
            typer.echo(f"- {title} :: {url}")


@app.command("publish")
def publish(platform: str, package: Path) -> None:
    publisher = build_publisher(platform)
    content_package = load_package(package)
    if platform not in content_package.platforms:
        raise typer.BadParameter(f"{platform} not found in package.")

    typer.echo(f"campaign_id: {content_package.campaign_id}")
    typer.echo(f"platform: {platform}")
    typer.echo("当前是接管脚手架模式，先输出 readiness 清单。")
    typer.echo("")
    typer.echo("\n".join(publisher.readiness_lines()))
    typer.echo("")
    typer.echo("下一步: 把该平台的 selector、检查点恢复和管理页验证写进正式发布器。")


def main() -> None:
    app()
