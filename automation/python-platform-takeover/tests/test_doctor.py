from __future__ import annotations

from social_publisher.doctor import format_doctor_report, run_doctor


def test_doctor_reports_placeholder_assets_as_warnings(tmp_path, monkeypatch) -> None:
    package_path = tmp_path / "content-package.local.yaml"
    package_path.write_text(
        "\n".join(
            [
                'campaign_id: "demo"',
                'theme: "demo"',
                "assets:",
                '  main_video: "/ABS/PATH/final_video.mp4"',
                '  cover_3_4: "/ABS/PATH/cover-3x4.jpg"',
                '  cover_4_3: "/ABS/PATH/cover-4x3.jpg"',
                "platforms:",
                "  wechat_channels:",
                '    title: "标题"',
                '    description: "正文"',
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BROWSER_CDP_URL", "http://127.0.0.1:9222")
    monkeypatch.setenv("DEFAULT_TAKEOVER_MODE", "existing-tab")

    report = run_doctor(package_path=package_path, platform_id="wechat_channels")
    lines = format_doctor_report(report)

    assert report.has_failures is False
    assert any("WARN assets.main_video: 仍是占位路径" in line for line in lines)
    assert any("OK   platform: wechat_channels" in line for line in lines)


def test_doctor_marks_missing_platform_as_failure(tmp_path, monkeypatch) -> None:
    package_path = tmp_path / "content-package.local.yaml"
    video_path = tmp_path / "video.mp4"
    video_path.write_text("demo", encoding="utf-8")
    package_path.write_text(
        "\n".join(
            [
                'campaign_id: "demo"',
                'theme: "demo"',
                "assets:",
                f'  main_video: "{video_path}"',
                "platforms:",
                "  weibo:",
                '    title: "标题"',
                '    description: "正文"',
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BROWSER_CDP_URL", raising=False)
    monkeypatch.delenv("DEFAULT_TAKEOVER_MODE", raising=False)

    report = run_doctor(package_path=package_path, platform_id="wechat_channels")

    assert report.has_failures is True
    assert any(
        check.name == "platform" and check.status == "fail"
        for check in report.checks
    )
