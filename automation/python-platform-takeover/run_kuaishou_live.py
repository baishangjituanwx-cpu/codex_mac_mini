#!/usr/bin/env python3
"""Direct kuaishou live publish - bypasses CLI receipt parsing bug."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the venv packages are on the path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault("BROWSER_CDP_URL", "http://localhost:9222")

from social_publisher.browser import BrowserController, BrowserSessionConfig
from social_publisher.content_package import load_package
from social_publisher.platforms import build_publisher
from social_publisher.publish_receipts import (
    PublishReceipt,
    load_raw_receipts,
    receipt_path_for,
    upsert_receipt,
)

PACKAGE_PATH = Path(__file__).parent / "configs" / "content-package.2026-05-30-ai-employee-no-rush-repost-before-receipt.kuaishou.yaml"
PLATFORM = "kuaishou"

def main():
    print(f"[kuaishou-live] Loading package: {PACKAGE_PATH}")
    content_package = load_package(PACKAGE_PATH)
    print(f"[kuaishou-live] campaign_id: {content_package.campaign_id}")
    print(f"[kuaishou-live] platform: {PLATFORM}")

    platform_content = content_package.platforms[PLATFORM]
    print(f"[kuaishou-live] title: {platform_content.title}")
    print(f"[kuaishou-live] description: {platform_content.description}")
    print(f"[kuaishou-live] video: {content_package.assets.main_video}")
    print(f"[kuaishou-live] cover_3_4: {content_package.assets.cover_3_4}")
    print()

    publisher = build_publisher(PLATFORM)
    config = BrowserSessionConfig(cdp_url=os.getenv("BROWSER_CDP_URL"))

    print("[kuaishou-live] Connecting to browser via CDP...")
    try:
        with BrowserController(config) as controller:
            print("[kuaishou-live] Browser connected. Starting publish flow...")
            result = publisher.publish(
                controller,
                platform_content,
                content_package.assets,
                dry_run=False,
            )
    except Exception as exc:
        print(f"status: failed")
        print(f"ok: False")
        print(f"message: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"status: {result.status}")
    print(f"ok: {result.ok}")
    print(f"message: {result.message}")
    if result.current_url:
        print(f"current_url: {result.current_url}")
    if result.management_url:
        print(f"management_url: {result.management_url}")
    if result.notes:
        print("notes:")
        for note in result.notes:
            print(f"  - {note}")

    # Write receipt if successful
    if result.ok and result.status.strip().lower() in {
        "submitted", "published", "under_review", "success", "verified",
    }:
        receipt = PublishReceipt(
            campaign_id=content_package.campaign_id,
            platform_id=PLATFORM,
            title=platform_content.title,
            status=result.status.strip().lower(),
            recorded_at=datetime.now(timezone.utc).isoformat(),
            current_url=result.current_url,
            management_url=result.management_url,
            notes=result.notes,
        )
        receipt_path = upsert_receipt(PACKAGE_PATH, receipt)
        print(f"receipt_path: {receipt_path}")
        print("[kuaishou-live] Receipt updated successfully.")
    else:
        print("[kuaishou-live] No receipt written (publish not confirmed).")

if __name__ == "__main__":
    main()
