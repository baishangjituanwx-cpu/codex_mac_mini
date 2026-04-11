from pathlib import Path

from social_publisher.content_package import load_package


def test_load_example_package() -> None:
    example_path = (
        Path(__file__).resolve().parents[1] / "configs" / "content-package.example.yaml"
    )
    package = load_package(example_path)
    assert package.campaign_id == "2026-04-11-ai-workflow"
    assert "wechat_channels" in package.platforms
