from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from app.api._demo_data import VULNERABILITY_CATALOG, DEMO_ASSETS, cvss_to_severity
router = APIRouter()

# Provenance marker surfaced by the UI. This endpoint serves SIMULATED records
# authored as internally consistent fixtures; it does not query a live scanner
# or external intelligence feed.
SOURCE_STATE = "simulated"

# Deterministic discovery timestamps: spread findings across a fixed window so
# repeated requests return identical data (no randomised drift).
_BASE_TIME = datetime(2024, 8, 1, 9, 0, 0)


def _build_vulnerabilities() -> list[dict]:
    # Expand the catalogue into per-asset findings. A finding is only created
    # for an asset that actually runs the affected component, so the CVE <->
    # component <-> asset relationship is always consistent. When an asset is not
    # present the vulnerability is still reported against an 'unassigned' asset
    # so no CVE silently disappears."
    findings: list[dict] = []
    idx = 0
    for entry in VULNERABILITY_CATALOG:
        component = entry["affected_component"]
        matching_assets = [a for a in DEMO_ASSETS if component in a.get("components", [])]

        # Primary finding: prefer a publicly exposed, high-criticality asset.
        if matching_assets:
            matching_assets.sort(
                key=lambda a: (a["publicly_exposed"], a["criticality"]), reverse=True
            )
            asset = matching_assets[0]
        else:
            asset = None
        # Lifecycle status is assigned deterministically so the counts are
        # stable and every severity band has a mix of states.
        if entry["cisa_kev"] and entry["exploit_available"]:
            status = "active"
        elif entry["cisa_kev"]:
            status = "in_triage"
        elif entry["cvss_score"] >= 9.0:
            status = "active"
        else:
            status = "in_triage" if idx % 3 == 0 else "fixed"

        findings.append(
            {
                "id": f"vuln-{idx}",
                "cve_id": entry["cve_id"],
                "title": entry["title"],
                "description": entry["description"],
                "cvss_score": entry["cvss_score"],
                "cvss_vector": entry["cvss_vector"],
                "severity": cvss_to_severity(entry["cvss_score"]),
                "cisa_kev": entry["cisa_kev"],
                "exploit_available": entry["exploit_available"],
                "affected_component": component,
                "installed_version": entry["installed_version"],
                "fixed_version": entry["fixed_version"],
                "ecosystem": entry["ecosystem"],
                "status": status,
                "asset_id": asset["id"] if asset else None,
                "asset_name": asset["name"] if asset else "unassigned",
                "publicly_exposed": bool(asset and asset["publicly_exposed"]),
                "discovered_at": (_BASE_TIME - timedelta(hours=idx * 7)).isoformat(),
                "updated_at": (_BASE_TIME - timedelta(hours=max(0, idx * 7 - 3))).isoformat(),
                "source_state": SOURCE_STATE,
            }
        )
        idx += 1
    return findings
DEMO_VULNERABILITIES = _build_vulnerabilities()


def _summary() -> dict:
    # Only "active" and "in_triage" represent unresolved work; "fixed" findings
    # are excluded from the open-severity counts the UI does not overstate
    # outstanding risk.
    open_vulns = [v for v in DEMO_VULNERABILITIES if v["status"] != "fixed"]
    return {
        "total": len(DEMO_VULNERABILITIES),
        "critical": len([v for v in open_vulns if v["severity"] == "critical"]),
        "high": len([v for v in open_vulns if v["severity"] == "high"]),
        "medium": len([v for v in open_vulns if v["severity"] == "medium"]),
        "low": len([v for v in open_vulns if v["severity"] == "low"]),
        "cisa_kev": len([v for v in DEMO_VULNERABILITIES if v["cisa_kev"]]),
        "exploit_available": len([v for v in DEMO_VULNERABILITIES if v["exploit_available"]]),
        "remediation_required": len(open_vulns),
        "fixed": len([v for v in DEMO_VULNERABILITIES if v["status"] == "fixed"]),
        "source_state": SOURCE_STATE,
    }

@router.get("/")
async def get_vulnerabilities(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    results = DEMO_VULNERABILITIES.copy()

    if severity:
        results = [v for v in results if v["severity"] == severity]
    if status:
        results = [v for v in results if v["status"] == status]
    if search:
        q = search.lower()
        results = [
            v for v in results
            if q in v["cve_id"].lower()
            or q in v["title"].lower()
            or q in (v["affected_component"] or "").lower()
            or q in (v["asset_name"] or "").lower()
        ]

    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": results[start:end],
        "total": total,
        "page": page,
        "page_size": page,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "source_state": SOURCE_STATE,
        "summary": _summary(),
    }

@router.get("/stats/overview")
async def get_vulnerability_stats():
    return _summary()

@router.get("/{vulnerability_id}")
async def get_vulnerability(vulnerability_id: str):
    for vuln in DEMO_VULNERABILITIES:
        if vuln["id"] == vulnerability_id:
            return vuln
    return {"error": "Vulnerability not found"}