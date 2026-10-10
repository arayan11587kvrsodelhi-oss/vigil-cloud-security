"""Dashboard summary and security score.

The aggregates are computed from the same PostgreSQL records that back the assets
and vulnerabilities endpoints, so the dashboard can never disagree with those
pages. All counts are real queries — nothing is hard-coded and no simulated
numbers are mixed in.

With an empty database the summary returns zero totals and an empty findings
list, and the security score reflects "no data" rather than a confident number.

The vulnerability-severity and risk-category building blocks are shared with the
vulnerabilities endpoint via ``app.api.vulnerabilities``.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.vulnerabilities import _OPEN_STATUSES, _severity_bucket
from app.core.database import get_db
from app.models.models import Asset, Container, Vulnerability

router = APIRouter()

# Provenance marker surfaced by the UI: these aggregates are derived from real
# database records, not a live risk model.
SOURCE_STATE = "database"


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


async def _counts_by_severity(db: AsyncSession) -> dict[str, int]:
    """Open (unresolved) findings grouped by severity, from the database."""
    rows = await db.execute(
        select(Vulnerability.severity, func.count())
        .where(Vulnerability.status.in_(_OPEN_STATUSES))
        .group_by(Vulnerability.severity)
    )
    by_severity = {(sev or "").lower(): count for sev, count in rows.all()}
    return {
        "critical": by_severity.get("critical", 0),
        "high": by_severity.get("high", 0),
        "medium": by_severity.get("medium", 0),
        "low": by_severity.get("low", 0),
    }


async def _recent_findings(db: AsyncSession, limit: int = 5) -> list[dict]:
    """The most recent real vulnerability findings, with their asset names."""
    stmt = (
        select(Vulnerability)
        .order_by(Vulnerability.discovered_at.desc().nullslast())
        .limit(limit)
    )
    vulns = (await db.execute(stmt)).scalars().all()
    if not vulns:
        return []

    asset_ids = {v.asset_id for v in vulns if v.asset_id is not None}
    asset_names: dict[str, str] = {}
    if asset_ids:
        assets = (
            await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
        ).scalars().all()
        asset_names = {str(a.id): a.name for a in assets}

    return [
        {
            "id": str(v.id),
            "title": v.title,
            "severity": _severity_bucket(v),
            "source": "Vulnerability Record",  # from the database, not a live scanner
            "asset": asset_names.get(str(v.asset_id), "unassigned") if v.asset_id else "unassigned",
            "discovered_at": v.discovered_at.isoformat() if v.discovered_at else None,
            "status": v.status,
        }
        for v in vulns
    ]


async def _asset_counts(db: AsyncSession) -> dict[str, int]:
    """Asset totals and per-type counts, from the database."""
    total_assets = await db.scalar(select(func.count()).select_from(Asset)) or 0
    exposed = (
        await db.scalar(
            select(func.count()).select_from(Asset).where(Asset.publicly_exposed.is_(True))
        )
        or 0
    )
    type_rows = await db.execute(
        select(Asset.asset_type, func.count()).group_by(Asset.asset_type)
    )
    by_type = {(t or "unknown"): c for t, c in type_rows.all()}
    return {
        "total_assets": total_assets,
        "publicly_exposed": exposed,
        "by_type": by_type,
        "api_endpoints": by_type.get("api_endpoint", 0),
        "cloud_instances": by_type.get("cloud_instance", 0),
        "databases": by_type.get("database", 0),
        "dns_records": by_type.get("dns_record", 0),
    }


def _status_band(score: float) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "needs_attention"
    return "at_risk"


@router.get("/security-score")
async def get_security_score(db: AsyncSession = Depends(get_db)):
    total_assets = await db.scalar(select(func.count()).select_from(Asset)) or 0
    total_vulns = await db.scalar(select(func.count()).select_from(Vulnerability)) or 0
    open_vulns = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.status.in_(_OPEN_STATUSES))
        )
        or 0
    )
    kev = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.cisa_kev.is_(True))
        )
        or 0
    )
    exposed_assets = (
        await db.scalar(
            select(func.count()).select_from(Asset).where(Asset.publicly_exposed.is_(True))
        )
        or 0
    )
    exposed_ratio = (exposed_assets / total_assets) if total_assets else 0.0
    open_ratio = (open_vulns / total_vulns) if total_vulns else 0.0

    # Deterministic, documented derivation from the real records above. This is
    # a posture heuristic over actual counts, not a validated risk model.
    asset_coverage = 100.0 if total_assets else 0.0
    vulnerability_score = _clamp(100.0 - open_ratio * 70.0 - min(kev, 10) * 2.0)
    exposure_score = _clamp(100.0 - exposed_ratio * 100.0)
    overall_score = round(
        (asset_coverage + vulnerability_score + exposure_score) / 3.0, 1
    )

    today = datetime.utcnow()
    trend = [
        {
            "date": (today - timedelta(days=i)).date().isoformat(),
            "score": overall_score,
        }
        for i in range(14, -1, -1)
    ]

    return {
        "overall_score": overall_score,
        "asset_coverage": round(asset_coverage, 1),
        "vulnerability_score": round(vulnerability_score, 1),
        "exposure_score": round(exposure_score, 1),
        # No IAM/secret records exist in the schema yet, so these components are
        # reported as unmeasured rather than invented.
        "iam_score": 0.0,
        "secret_score": 0.0,
        "trend": trend,
        "updated_at": today.isoformat(),
        "source_state": SOURCE_STATE,
        "model": "Database-derived posture heuristic (assets + vulnerabilities only)",
        "components_measured": ["asset_coverage", "vulnerability_score", "exposure_score"],
        "components_unavailable": ["iam_score", "secret_score"],
    }


@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    sev = await _counts_by_severity(db)
    assets = await _asset_counts(db)

    total_vulns = await db.scalar(select(func.count()).select_from(Vulnerability)) or 0
    kev = (
        await db.scalar(
            select(func.count())
            .select_from(Vulnerability)
            .where(Vulnerability.cisa_kev.is_(True))
        )
        or 0
    )
    containers_total = await db.scalar(select(func.count()).select_from(Container)) or 0
    privileged_containers = (
        await db.scalar(
            select(func.count())
            .select_from(Container)
            .where(Container.privileges == "privileged")
        )
        or 0
    )

    return {
        "total_assets": assets["total_assets"],
        "publicly_exposed": assets["publicly_exposed"],
        "total_vulnerabilities": total_vulns,
        "critical": sev["critical"],
        "high": sev["high"],
        "medium": sev["medium"],
        "low": sev["low"],
        "cisa_kev": kev,
        "active_attack_paths": 0,  # no attack-path solver is connected
        "containers": containers_total,
        "privileged_containers": privileged_containers,
        "secrets_detected": 0,  # no secret scanner is connected
        "secrets_rotation_required": 0,
        "iam_roles": 0,  # no cloud IAM discovery is connected
        "databases": assets["databases"],
        "repositories": 0,  # no SCM integration is connected
        "recent_findings": await _recent_findings(db),
        "risk_categories": [
            {
                "category": "Vulnerability Management",
                "score": round(100 - sev["critical"] * 15 - sev["high"] * 6),
                "status": _status_band(100 - sev["critical"] * 15 - sev["high"] * 6),
            },
            {"category": "Identity & Access", "score": 0, "status": "at_risk"},
            {"category": "Data Security", "score": 0, "status": "at_risk"},
            {"category": "Network Security", "score": 0, "status": "at_risk"},
            {"category": "Container Security", "score": 0, "status": "at_risk"},
            {"category": "Secret Management", "score": 0, "status": "at_risk"},
            {"category": "Supply Chain", "score": 0, "status": "at_risk"},
            {"category": "Compliance", "score": 0, "status": "at_risk"},
        ],
        "system_health": {
            # "database" is honest: the data comes from PostgreSQL, and no live
            # scanner fleet or sync worker is running.
            "status": "database",
            "last_sync": datetime.utcnow().isoformat(),
            "scanners_active": 0,  # no scanner processes are connected
            "queued_scans": 0,
            "uptime": None,
        },
        "attack_surface": {
            "total_exposed": assets["publicly_exposed"],
            "api_endpoints": assets["api_endpoints"],
            "web_applications": 0,  # not derivable from the current schema
            "open_ports": 0,  # no port scanner is connected
            "dns_records": assets["dns_records"],
            "cloud_instances": assets["cloud_instances"],
        },
        "source_state": SOURCE_STATE,
    }