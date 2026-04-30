from pathlib import Path

from social_publisher.publish_receipts import (
    clear_receipt,
    get_receipt,
    load_receipts,
    PublishReceipt,
    receipt_path_for,
    should_block_republish,
    upsert_receipt,
)


def test_receipt_roundtrip(tmp_path: Path) -> None:
    package = tmp_path / "automation" / "configs" / "content-package.test.yaml"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text("campaign_id: test\n", encoding="utf-8")

    receipt = PublishReceipt(
        campaign_id="2026-04-23-demo",
        platform_id="xiaohongshu",
        title="先替平台执行：别再手动回填字段",
        status="submitted",
        recorded_at="2026-04-23T06:00:00+00:00",
        current_url="https://creator.xiaohongshu.com/publish/success",
        management_url="https://creator.xiaohongshu.com/new/note-manager?source=official",
        notes=["share_link captured"],
    )

    receipt_path = upsert_receipt(package, receipt)
    loaded = get_receipt(package, "2026-04-23-demo", "xiaohongshu")

    assert receipt_path == receipt_path_for(package, "2026-04-23-demo")
    assert loaded is not None
    assert loaded.platform_id == "xiaohongshu"
    assert loaded.title == "先替平台执行：别再手动回填字段"
    assert loaded.current_url == "https://creator.xiaohongshu.com/publish/success"
    assert loaded.notes == ["share_link captured"]


def test_should_block_republish_only_for_success_like_statuses() -> None:
    blocking = PublishReceipt(
        campaign_id="2026-04-23-demo",
        platform_id="xiaohongshu",
        title="title",
        status="published",
        recorded_at="2026-04-23T06:00:00+00:00",
    )
    missing = PublishReceipt(
        campaign_id="2026-04-23-demo",
        platform_id="xiaohongshu",
        title="title",
        status="unconfirmed",
        recorded_at="2026-04-23T06:00:00+00:00",
    )

    assert should_block_republish(blocking) is True
    assert should_block_republish(missing) is False
    assert should_block_republish(None) is False


def test_should_block_republish_for_cover_repair_review_status() -> None:
    repair_pending = PublishReceipt(
        campaign_id="2026-04-24-demo",
        platform_id="wechat_channels",
        title="title",
        status="verified_cover_repair_under_review",
        recorded_at="2026-04-24T10:00:00+00:00",
    )

    assert should_block_republish(repair_pending) is True


def test_should_block_republish_for_account_review_pending_status() -> None:
    review_pending = PublishReceipt(
        campaign_id="2026-04-30-demo",
        platform_id="toutiao",
        title="title",
        status="blocked_account_review_pending",
        recorded_at="2026-04-30T10:00:00+00:00",
    )

    assert should_block_republish(review_pending) is True


def test_load_receipts_accepts_legacy_receipts_without_title(tmp_path: Path) -> None:
    package = tmp_path / "automation" / "configs" / "content-package.test.yaml"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text("campaign_id: test\n", encoding="utf-8")
    path = receipt_path_for(package, "2026-04-29-demo")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
{
  "campaign_id": "2026-04-29-demo",
  "receipts": {
    "kuaishou": {
      "campaign_id": "2026-04-29-demo",
      "platform_id": "kuaishou",
      "status": "under_review",
      "recorded_at": "2026-04-29T07:31:10.607Z"
    }
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    receipts = load_receipts(package, "2026-04-29-demo")

    assert receipts["kuaishou"].title == ""
    assert should_block_republish(receipts["kuaishou"]) is True


def test_load_receipts_ignores_unknown_metadata_fields(tmp_path: Path) -> None:
    package = tmp_path / "automation" / "configs" / "content-package.test.yaml"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text("campaign_id: test\n", encoding="utf-8")
    path = receipt_path_for(package, "2026-04-30-demo")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
{
  "campaign_id": "2026-04-30-demo",
  "receipts": {
    "toutiao": {
      "campaign_id": "2026-04-30-demo",
      "platform_id": "toutiao",
      "title": "title",
      "status": "blocked_account_review_pending",
      "recorded_at": "2026-04-30T22:30:11+08:00",
      "verified_fields": {
        "account_status_text": "账号信息审核中"
      },
      "object_nonce": "nonce"
    }
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    receipts = load_receipts(package, "2026-04-30-demo")

    assert receipts["toutiao"].status == "blocked_account_review_pending"
    assert should_block_republish(receipts["toutiao"]) is True


def test_clear_receipt_removes_file_when_campaign_becomes_empty(tmp_path: Path) -> None:
    package = tmp_path / "automation" / "configs" / "content-package.test.yaml"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text("campaign_id: test\n", encoding="utf-8")
    receipt = PublishReceipt(
        campaign_id="2026-04-23-demo",
        platform_id="xiaohongshu",
        title="title",
        status="submitted",
        recorded_at="2026-04-23T06:00:00+00:00",
    )
    path = upsert_receipt(package, receipt)

    removed = clear_receipt(package, "2026-04-23-demo", "xiaohongshu")

    assert removed is True
    assert not path.exists()
