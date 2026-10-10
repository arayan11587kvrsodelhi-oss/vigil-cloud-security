"""Live smoke check against the configured PostgreSQL database.

This is a manual verification helper (not part of the pytest suite). It:

1. Reports the row count of every VIGIL table.
2. Calls the database-backed endpoints through the real ASGI app (no server
   needed) and prints what they return, so an empty database can be confirmed to
   produce empty collections and zero totals rather than simulated records.
3. Optionally creates one asset, so you can verify persistence across a restart
   (see the README / final report procedure).

Run from the backend directory with the virtualenv active:

    python scripts/smoke_check.py
    python scripts/smoke_check.py --create-asset
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.models import Asset  # noqa: E402

TABLES = [
    "assets",
    "vulnerabilities",
    "attack_paths",
    "containers",
    "iam_roles",
    "network_routes",
    "secrets",
    "scan_results",
]

ENDPOINTS = [
    "/api/v1/assets/",
    "/api/v1/assets/types/summary",
    "/api/v1/vulnerabilities/",
    "/api/v1/vulnerabilities/stats/overview",
    "/api/v1/dashboard/summary",
    "/api/v1/dashboard/security-score",
]


async def _row_counts() -> None:
    async with engine.connect() as conn:
        print("--- table row counts ---")
        for table in TABLES:
            count = await conn.scalar(text(f"SELECT count(*) FROM {table}"))
            print(f"  {table:<16} {count}")


async def _endpoint_probe() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://smoke") as client:
        print("--- endpoint responses ---")
        for path in ENDPOINTS:
            resp = await client.get(path)
            body = resp.json()
            # Print only the headline numbers so credentials/data are not dumped.
            if isinstance(body, dict):
                if "source_state" not in body:
                    # e.g. the asset type-summary map: show it as-is.
                    print(f"  GET {path} -> {resp.status_code} {body}")
                    continue
                keys = ["total", "items", "publicly_exposed", "source_state", "overall_score"]
                summary = {
                    k: (len(v) if k == "items" and isinstance(v, list) else v)
                    for k, v in body.items()
                    if k in keys
                }
                if isinstance(body.get("summary"), dict):
                    summary["summary.total"] = body["summary"].get("total")
                print(f"  GET {path} -> {resp.status_code} {summary}")
            else:
                print(f"  GET {path} -> {resp.status_code} {body}")


async def _create_asset() -> None:
    from datetime import datetime

    from app.core.database import async_session_factory

    async with async_session_factory() as session:
        asset = Asset(
            name="smoke-test-asset",
            asset_type="cloud_instance",
            provider="aws",
            region="us-east-1",
            publicly_exposed=False,
            criticality=3,
            tags=["smoke-test"],
            asset_metadata={},
            discovered_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True,
        )
        session.add(asset)
        await session.commit()
        print(f"--- created asset id={asset.id} (name=smoke-test-asset) ---")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--create-asset",
        action="store_true",
        help="Insert one smoke-test asset to verify persistence across a restart.",
    )
    args = parser.parse_args()

    try:
        await _row_counts()
    except Exception as exc:  # noqa: BLE001
        print(f"Database unavailable: {exc}")
        raise

    await _endpoint_probe()

    if args.create_asset:
        await _create_asset()
        await _endpoint_probe()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
