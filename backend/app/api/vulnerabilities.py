"""Vulnerability findings API.

Findings are read from PostgreSQL via the shared async SQLAlchemy engine/session.
The response shape is preserved from the previous fixture-based implementation so
the frontend contract does not change, but every value is derived from actual
``vulnerabilities`` and ``assets`` rows.

When the ``vulnerabilities`` table is empty the endpoints return empty
collections and zero totals — they never substitute simulated records. Demo
fixtures are only returned when an operator explicitly sets ``ENABLE_DEMO_MODE``,
and those responses are tagged as ``simulated``.

Note on pagination: ``total`` is the number of rows matching the applied filters
(before pagination), and ``page_size`` echoes the requested page size. These are
intentionally different values and the frontend treats them as such.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api._demo_data import demo_mode_enabled, simulated_response
from app.core.database import get_db
from app.models.models import Asset, Vulnerability

router = APIRouter()

# Provenance marker surfaced by the UI: these findings are real database content,
# not the output of a live scanner or external intelligence feed.
SOURCE_STATE = "database"

# Only "active" and "in_triage" represent unresolved work; other statuses are
# excluded from the open-severity counts so the UI does not overstate risk.
_OPEN_STATUSES = ("active", "in_triage")
_SEVERITY_BUCKETS = ("critical", "high", "medium", "low")


def _severity_bucket(vuln: Vulnerability) -> str:
    """Classify a row into a UI severity bucket, falling back to CVSS score."""
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


def _serialize(vuln: Vulnerability, asset_name: Optional[str]) -> dict:
    """Serialize a vulnerability row into the frontend contract.

    ``asset_name`` is supplied by the caller from a batched lookup so this never
    issues a per-row query (no N+1).
    """
    return {
        "id": str(vuln.id),
        "cve_id": vuln.cve_id,
        "title": vuln.title,
        "description": vuln.description,
        "cvss_score": vuln.cvss_score,
        "cvss_vector": vuln.cvss_vector,
        "severity": _severity_bucket(vuln),
        "cisa_kev": bool(vuln.cisa_kev),
        "exploit_available": bool(vuln.exploit_available),
        "affected_component": vuln.affected_component,
        "fixed_version": vuln.fixed_version,
        "status": vuln.status,
        "asset_id": str(vuln.asset_id) if vuln.asset_id else None,
        "asset_name": asset_name or "unassigned",
        "publicly_exposed": False,  # enriched by the caller when the asset is known
        "discovered_at": vuln.discovered_at.isoformat() if vuln.discovered_at else None,
        "updated_at": vuln.updated_at.isoformat() if vuln.updated_at else None,
        "source_state": SOURCE_STATE,
    }


async def _asset_lookup(db: AsyncSession, vulns: list[Vulnerability]) -> dict[str, Asset]:
    """Load the distinct assets referenced by ``vulns`` in a single query."""
    asset_ids = {v.asset_id for v in vulns if v.asset_id is not None}
    if not asset_ids:
        return {}
    result = await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
    return {str(a.id): a for a in result.scalars().all()}


async def _summary(db: AsyncSession) -> dict:
    """Compute the vulnerability summary from database aggregates.

    Uses grouped scalar queries rather than loading every row, so the summary
    stays cheap on large tables.
    """
    total = await db.scalar(select(func.count()).select_from(Vulnerability)) or 0

    severity_rows = await db.execute(
        select(Vulnerability.severity, func.count())
        .where(Vulnerability.status.in_(_OPEN_STATUSES))
        .group_by(Vulnerability.severity)
    )
    by_severity = {(sev or "").lower(): count for sev, count in severity_rows.all()}

    cisa_kev = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.cisa_kev.is_(True))
        )
        or 0
    )
    exploit_available = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.exploit_available.is_(True))
        )
        or 0
    )
    remediation_required = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.status.in_(_OPEN_STATUSES))
        )
        or 0
    )
    fixed = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.status == "fixed")
        )
        or 0
    )

    return {
        "total": total,
        "critical": by_severity.get("critical", 0),
        "high": by_severity.get("high", 0),
        "medium": by_severity.get("medium", 0),
        "low": by_severity.get("low", 0),
        "cisa_kev": cisa_kev,
        "exploit_available": exploit_available,
        "remediation_required": remediation_required,
        "fixed": fixed,
        "source_state": SOURCE_STATE,
    }


async def _demo_vulnerabilities() -> list[dict]:
    """Return the labelled simulated fallback findings (dev only).

    Delegates to the fixture builder in ``_demo_data`` so demo mode is the single
    place the legacy catalogue is expanded.
    """
    from app.api._demo_data import build_demo_vulnerabilities

    return build_demo_vulnerabilities()


async def _demo_summary() -> dict:
    items = await _demo_vulnerabilities()
    open_vulns = [v for v in items if v["status"] in _OPEN_STATUSES]
    return {
        "total": len(items),
        "critical": len([v for v in open_vulns if v["severity"] == "critical"]),
        "high": len([v for v in open_vulns if v["severity"] == "high"]),
        "medium": len([v for v in open_vulns if v["severity"] == "medium"]),
        "low": len([v for v in open_vulns if v["severity"] == "low"]),
        "cisa_kev": len([v for v in items if v["cisa_kev"]]),
        "exploit_available": len([v for v in items if v["exploit_available"]]),
        "remediation_required": len(open_vulns),
        "fixed": len([v for v in items if v["status"] == "fixed"]),
        "source_state": "simulated",
    }


@router.get("/")
async def get_vulnerabilities(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    if demo_mode_enabled():
        items = await _demo_vulnerabilities()
        if severity:
            items = [v for v in items if v["severity"] == severity]
        if status:
            items = [v for v in items if v["status"] == status]
        if search:
            q = search.lower()
            items = [
                v
                for v in items
                if q in (v["cve_id"] or "").lower()
                or q in (v["title"] or "").lower()
                or q in (v["affected_component"] or "").lower()
                or q in (v["asset_name"] or "").lower()
            ]
        total = len(items)
        start = (page - 1) * page_size
        return simulated_response(
            {
                "items": items[start : start + page_size],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": max(1, (total + page_size - 1) // page_size) if total else 0,
                "summary": await _demo_summary(),
            }
        )

    # Filter predicates reused for both the count and the page query. The count
    # is computed before pagination so `total` reflects every matching row.
    filters = []
    if severity:
        filters.append(func.lower(Vulnerability.severity) == severity.lower())
    if status:
        filters.append(Vulnerability.status == status)
    if search:
        like = f"%{search}%"
        filters.append(
            or_(
                Vulnerability.cve_id.ilike(like),
                Vulnerability.title.ilike(like),
                Vulnerability.affected_component.ilike(like),
            )
        )

    total = (
        await db.scalar(select(func.count()).select_from(Vulnerability).where(*filters)) or 0
    )

    stmt = (
        select(Vulnerability)
        .where(*filters)
        .order_by(
            Vulnerability.discovered_at.desc().nullslast(), Vulnerability.title.asc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(stmt)).scalars().all()

    # One batched asset lookup for the whole page (no N+1).
    assets = await _asset_lookup(db, list(rows))
    items = []
    for vuln in rows:
        asset = assets.get(str(vuln.asset_id)) if vuln.asset_id else None
        payload = _serialize(vuln, asset.name if asset else None)
        payload["publicly_exposed"] = bool(asset.publicly_exposed) if asset else False
        items.append(payload)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size) if total else 0,
        "source_state": SOURCE_STATE,
        "summary": await _summary(db),
    }


@router.get("/stats/overview")
async def get_vulnerability_stats(db: AsyncSession = Depends(get_db)):
    if demo_mode_enabled():
        return simulated_response(await _demo_summary())
    return await _summary(db)


@router.get("/{vulnerability_id}")
async def get_vulnerability(vulnerability_id: str, db: AsyncSession = Depends(get_db)):
    if not demo_mode_enabled():
        try:
            vuln_uuid = UUID(vulnerability_id)
        except (ValueError, AttributeError, TypeError):
            raise HTTPException(status_code=404, detail="Vulnerability not found")

        vuln = await db.get(Vulnerability, vuln_uuid)
        if vuln is None:
            raise HTTPException(status_code=404, detail="Vulnerability not found")

        assets = await _asset_lookup(db, [vuln])
        asset = assets.get(str(vuln.asset_id)) if vuln.asset_id else None
        payload = _serialize(vuln, asset.name if asset else None)
        payload["publicly_exposed"] = bool(asset.publicly_exposed) if asset else False
        return payload

    for vuln in await _demo_vulnerabilities():
        if vuln["id"] == vulnerability_id:
            return vuln
    raise HTTPException(status_code=404, detail="Vulnerability not found")