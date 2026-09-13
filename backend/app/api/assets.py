from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from app.api._demo_data import DEMO_ASSETS as _ASSET_FIXTURES, VULNERABILITY_CATALOG, cvss_to_severity
router = APIRouter()

# Provenance marker surfaced by the UI: SIMULATED asset inventory, not the
# output of live cloud-provider discovery.
SOURCE_STATE = "simulated"

# Pre-compute per-asset vulnerability rollups from the catalogue so the asset
# list and the vulnerability list can never disagree.
_COMPONENT_INDEX: dict[str, list[dict]] = {}
for _entry in VULNERABILITY_CATALOG:
    _COMPONENT_INDEX.setdefault(_entry["affected_component"], []).append(_entry)

_BASE_TIME = datetime(2024, 8, 1, 9, 0, 0)


def _serialize_asset(asset: dict, idx: int) -> dict:
    vulns = []
    for component in asset.get("components", []):
        vulns.extend(_COMPONENT_INDEX.get(component, []))

    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        by_severity[cvss_to_severity(v["cvss_score"])] += 1
    return {
        **{k: v for k, v in asset.items() if k != "components"},
        "discovered_at": (_BASE_TIME - timedelta(days=120 - idx * 6)).isoformat(),
        "last_seen_at": (_BASE_TIME - timedelta(minutes=idx * 7)).isoformat(),
        "is_active": True,
        "vulnerability_count": len(vulns),
        "vulnerability_severity": by_severity,
        "critical_vulnerabilities": by_severity["critical"],
        "open_findings": len([v for v in vulns if v["cisa_kev"] or v["exploit_available"]]),
        "source_state": SOURCE_STATE,
    }

DEMO_ASSETS = [_serialize_asset(a, i) for i, a in enumerate(_ASSET_FIXTURES)]

@router.get("/")
async def get_assets(
    asset_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    results = DEMO_ASSETS.copy()

    if asset_type:
        results = [a for a in results if a["asset_type"] == asset_type]
    if search:
        results = [a for a in results if search.lower() in a["name"].lower()]

    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": results[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "publicly_exposed": len([a for a in results if a["publicly_exposed"]]),
        "source_state": SOURCE_STATE,
    }

@router.get("/types/summary")
async def get_asset_type_summary():
    summary: dict[str, dict[str, int]] = {}
    for asset in DEMO_ASSETS:
        t = asset["asset_type"]
        if t not in summary:
            summary[t] = {"count": 0, "exposed": 0, "critical": 0, "vulnerabilities": 0}
        summary[t]["count"] += 1
        if asset["publicly_exposed"]:
            summary[t]["exposed"] += 1
        if asset["criticality"] >= 7:
            summary[t]["critical"] += 1
        summary[t]["vulnerabilities"] += asset["vulnerability_count"]
    return summary
@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    for asset in DEMO_ASSETS:
        if asset["id"] == asset_id:
            return asset
    return {"error": "Asset not found"}