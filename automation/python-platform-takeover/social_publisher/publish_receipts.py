from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


BLOCKING_RECEIPT_STATUSES = frozenset(
    {
        "submitted",
        "published",
        "under_review",
        "success",
        "verified",
        "cover_repair_under_review",
        "verified_cover_repair_under_review",
    }
)


@dataclass
class PublishReceipt:
    campaign_id: str
    platform_id: str
    title: str
    status: str
    recorded_at: str
    current_url: str | None = None
    management_url: str | None = None
    external_id: str | None = None
    share_link: str | None = None
    notes: list[str] = field(default_factory=list)


def receipt_dir_for(package_path: str | Path) -> Path:
    package = Path(package_path).resolve()
    return package.parents[1] / "state" / "publish-receipts"


def receipt_path_for(package_path: str | Path, campaign_id: str) -> Path:
    return receipt_dir_for(package_path) / f"{campaign_id}.json"


def load_receipts(package_path: str | Path, campaign_id: str) -> dict[str, PublishReceipt]:
    path = receipt_path_for(package_path, campaign_id)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    receipts_payload = payload.get("receipts", {})
    receipts: dict[str, PublishReceipt] = {}
    if not isinstance(receipts_payload, dict):
        return receipts
    for platform_id, item in receipts_payload.items():
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        normalized.setdefault("title", "")
        receipts[platform_id] = PublishReceipt(**normalized)
    return receipts


def get_receipt(
    package_path: str | Path,
    campaign_id: str,
    platform_id: str,
) -> PublishReceipt | None:
    return load_receipts(package_path, campaign_id).get(platform_id)


def should_block_republish(receipt: PublishReceipt | None) -> bool:
    if receipt is None:
        return False
    status = receipt.status.strip().lower()
    if status in BLOCKING_RECEIPT_STATUSES:
        return True
    return status.endswith("_cover_repair_under_review")


def upsert_receipt(
    package_path: str | Path,
    receipt: PublishReceipt,
) -> Path:
    path = receipt_path_for(package_path, receipt.campaign_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    receipts = load_raw_receipts(path)
    receipts[receipt.platform_id] = asdict(receipt)
    payload = {
        "campaign_id": receipt.campaign_id,
        "receipts": receipts,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def clear_receipt(
    package_path: str | Path,
    campaign_id: str,
    platform_id: str,
) -> bool:
    path = receipt_path_for(package_path, campaign_id)
    if not path.exists():
        return False
    receipts = load_raw_receipts(path)
    if platform_id not in receipts:
        return False
    receipts.pop(platform_id, None)
    if receipts:
        payload = {
            "campaign_id": campaign_id,
            "receipts": receipts,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        path.unlink()
    return True


def load_raw_receipts(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    receipts_payload = payload.get("receipts", {})
    if not isinstance(receipts_payload, dict):
        return {}
    return {
        platform_id: item
        for platform_id, item in receipts_payload.items()
        if isinstance(item, dict)
    }
