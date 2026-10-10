"""Asset inventory API.

Assets are read from PostgreSQL via the shared async SQLAlchemy engine/session.
The response shape is preserved from the previous fixture-based implementation so
the frontend contract does not change, but every value is derived from actual
``assets`` and ``vulnerabilities`` rows.

When the ``assets`` table is empty the endpoints return empty collections and
zero totals — they never substitute simulated records. Demo fixtures are only
returned when an operator explicitly sets ``ENABLE_DEMO_MODE``, and those
responses are tagged as ``simulated``.

Note on pagination: ``total`` is the number of rows matching the applied filters
(before pagination), and ``page_size`` echoes the requested page size. These are
intentionally different values and the frontend treats them as such.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api._demo_data import (
    DEMO_ASSETS as _DEMO_ASSET_FIXTURES,
    demo_mode_enabled,
    simulated_response,
)
from app.core.database import get_db
from app.models.models import Asset, Vulnerability

router = APIRouter()

# Provenance marker surfaced by the UI: the asset inventory is real database
# content, not the output of live cloud-provider discovery.
SOURCE_STATE = "database"

# Canonical severity buckets the UI consumes for per-asset rollups.
_SEVERITY_BUCKETS = ("critical", "high", "medium", "low")

# The shared vulnerability summary treats these statuses as unresolved work.
_OPEN_STATUSES = ("active", "in_triage")


def _severity_bucket(vuln: Vulnerability) -> str:
    """Classify a vulnerability row into a UI severity bucket.

    Prefers an explicit ``severity`` column value and falls back to the CVSS
    score when the column is empty, so a row with only a CVSS score still rolls
    up correctly.
    """
    severity = (vuln.severity or "").lower()
    if severity in _SEVERITY_BUCKETS or severity == "info":
        return severity
    score = vuln.cvss_score
    if score is None:
        return "info"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


def _serialize_asset(asset: Asset, vulns: list[Vulnerability]) -> dict:
    """Build the asset payload plus its vulnerability rollup.

    ``vulns`` are the rows already loaded for this asset (batched by the caller)
    so serialization never triggers a per-asset query.
    """
    by_severity = {bucket: 0 for bucket in _SEVERITY_BUCKETS}
    for vuln in vulns:
        bucket = _severity_bucket(vuln)
        if bucket in by_severity:
            by_severity[bucket] += 1

    open_findings = len(
        [v for v in vulns if (v.status or "").lower() in _OPEN_STATUSES]
    )
    return {
        "id": str(asset.id),
        "name": asset.name,
        "asset_type": asset.asset_type,
        "provider": asset.provider,
        "region": asset.region,
        "ip_address": asset.ip_address,
        "domain": asset.domain,
        "publicly_exposed": bool(asset.publicly_exposed),
        "criticality": asset.criticality,
        "tags": asset.tags or [],
        "metadata": asset.asset_metadata or {},
        "discovered_at": asset.discovered_at.isoformat() if asset.discovered_at else None,
        "last_seen_at": asset.last_seen_at.isoformat() if asset.last_seen_at else None,
        "is_active": bool(asset.is_active),
        "vulnerability_count": len(vulns),
        "vulnerability_severity": by_severity,
        "critical_vulnerabilities": by_severity["critical"],
        "open_findings": open_findings,
        "source_state": SOURCE_STATE,
    }


async def _fetch_assets_with_vulns(
    db: AsyncSession, assets: list[Asset]
) -> dict[str, list[Vulnerability]]:
    """Load all vulnerabilities for the given assets in a single query.

    Avoids the N+1 pattern: one query total regardless of how many assets are on
    the page.
    """
    if not assets:
        return {}
    asset_ids = [a.id for a in assets]

    result = await db.execute(
        select(Vulnerability).where(Vulnerability.asset_id.in_(asset_ids))
    )
    rows = result.scalars().all()

    grouped: dict[str, list[Vulnerability]] = {str(a.id): [] for a in assets}
    for vuln in rows:
        if vuln.asset_id is not None:
            grouped.setdefault(str(vuln.asset_id), []).append(vuln)
    return grouped


def _demo_assets() -> list[dict]:
    """Return the labelled simulated fallback inventory (dev only)."""
    return [simulated_response(a) for a in _DEMO_ASSET_FIXTURES]


@router.get("/")
async def get_assets(
    asset_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    if demo_mode_enabled():
        items = _demo_assets()
        if asset_type:
            items = [a for a in items if a["asset_type"] == asset_type]
        if search:
            items = [a for a in items if search.lower() in a["name"].lower()]
        total = len(items)
        start = (page - 1) * page_size
        return simulated_response(
            {
                "items": items[start : start + page_size],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": max(1, (total + page_size - 1) // page_size) if total else 0,
                "publicly_exposed": len([a for a in items if a["publicly_exposed"]]),
            }
        )

    # Base filter predicates reused for both the count and the page query.
    filters = []
    if asset_type:
        filters.append(Asset.asset_type == asset_type)
    if search:
        filters.append(Asset.name.ilike(f"%{search}%"))

    total = await db.scalar(select(func.count()).select_from(Asset).where(*filters)) or 0

    # Summary values are computed across ALL matching assets, not just the page.
    publicly_exposed = (
        await db.scalar(
            select(func.count())
            .select_from(Asset)
            .where(*filters, Asset.publicly_exposed.is_(True))
        )
        or 0
    )

    stmt = (
        select(Asset)
        .where(*filters)
        .order_by(Asset.discovered_at.desc().nullslast(), Asset.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    assets = (await db.execute(stmt)).scalars().all()

    vulns_by_asset = await _fetch_assets_with_vulns(db, list(assets))

    return {
        "items": [_serialize_asset(a, vulns_by_asset.get(str(a.id), [])) for a in assets],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size) if total else 0,
        "publicly_exposed": publicly_exposed,
        "source_state": SOURCE_STATE,
    }


@router.get("/types/summary")
async def get_asset_type_summary(db: AsyncSession = Depends(get_db)):
    if demo_mode_enabled():
        summary: dict[str, dict[str, int]] = {}
        for asset in _demo_assets():
            bucket = summary.setdefault(
                asset["asset_type"],
                {"count": 0, "exposed": 0, "critical": 0, "vulnerabilities": 0},
            )
            bucket["count"] += 1
            if asset["publicly_exposed"]:
                bucket["exposed"] += 1
            if asset["criticality"] >= 7:
                bucket["critical"] += 1
            bucket["vulnerabilities"] += asset["vulnerability_count"]
        return summary

    assets = (await db.execute(select(Asset))).scalars().all()
    vulns_by_asset = await _fetch_assets_with_vulns(db, list(assets))

    summary: dict[str, dict[str, int]] = {}
    for asset in assets:
        bucket = summary.setdefault(
            asset.asset_type or "unknown",
            {"count": 0, "exposed": 0, "critical": 0, "vulnerabilities": 0},
        )
        bucket["count"] += 1
        if asset.publicly_exposed:
            bucket["exposed"] += 1
        if (asset.criticality or 0) >= 7:
            bucket["critical"] += 1
        bucket["vulnerabilities"] += len(vulns_by_asset.get(str(asset.id), []))
    return summary


@router.get("/{asset_id}")
async def get_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    if not demo_mode_enabled():
        try:
            asset_uuid = UUID(asset_id)
        except (ValueError, AttributeError, TypeError):
            raise HTTPException(status_code=404, detail="Asset not found")

        asset = await db.get(Asset, asset_uuid)
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found")

        vulns_by_asset = await _fetch_assets_with_vulns(db, [asset])
        return _serialize_asset(asset, vulns_by_asset.get(str(asset.id), []))

    for asset in _demo_assets():
        if asset["id"] == asset_id:
            return asset
    raise HTTPException(status_code=404, detail="Asset not found")