from __future__ import annotations

import os

from social_publisher.env import load_dotenv_if_present


def test_load_dotenv_if_present_reads_current_working_directory(
    monkeypatch,
    tmp_path,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "BROWSER_CDP_URL=http://127.0.0.1:9222\nDEFAULT_TAKEOVER_MODE=existing-tab\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BROWSER_CDP_URL", raising=False)
    monkeypatch.delenv("DEFAULT_TAKEOVER_MODE", raising=False)

    loaded = load_dotenv_if_present()

    assert loaded == env_path
    assert os.getenv("BROWSER_CDP_URL") == "http://127.0.0.1:9222"
    assert os.getenv("DEFAULT_TAKEOVER_MODE") == "existing-tab"
