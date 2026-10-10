from fastapi import APIRouter
from datetime import datetime, timedelta
router = APIRouter()

# Provenance marker surfaced by the UI. Scan history is SIMULATED; no scanner
# actually executes against infrastructure in this build. This endpoint is NOT
# database-backed: the scan_results table would only ever hold records produced by
# a real scanner run, and none exists, so it is left empty rather than seeded with
# fabricated scan history. Every response is tagged simulated=True.
SOURCE_STATE = "simulated"

_BASE_TIME = datetime(2024, 8, 1, 9, 0, 0)

# Deterministic scan history. Each record only carries metadata the model can
# actually justify: status, timing, and finding counts. Duration is derived from
# start/complete timestamps rather than invented independently.
# (scan_type, status, target, findings(total,critical,high,medium,low), started_hours_ago, duration_minutes, failure_reason)
_RAW_SCANS = [
    ("secret", "completed", "all-repositories", (11, 3, 4, 4, 0), 2, 6, None),
    ("dependency", "completed", "all-repositories", (24, 5, 9, 7, 3), 3, 18, None),
    ("container", "completed", "production-cluster", (9, 2, 4, 2, 1), 5, 12, None),
    ("sbom", "completed", "payment-service", (6, 1, 2, 2, 1), 8, 9, None),
    ("dependency", "completed", "api-gateway", (14, 4, 6, 3, 1), 12, 15, None),
    ("secret", "completed", "api-gateway", (3, 1, 2, 0, 0), 16, 5, None),
    ("container", "running", "production-cluster", (4, 1, 1, 1, 1), 0, None, None),
    ("dependency", "queued", "all-repositories", (0, 0, 0, 0, 0), 0, None, None),
    ("sbom", "queued", "web-app", (0, 0, 0, 0, 0), 0, None, None),
    ("dependency", "failed", "legacy-billing", (0, 0, 0, 0, 0), 20, None, "Dependency resolver timed out after 300s (simulated)"),
    ("container", "failed", "ml-training-worker", (0, 0, 0, 0, 0), 30, None, "Registry authentication failed (simulated)"),
    ("secret", "completed", "infrastructure", (2, 0, 1, 1, 0), 36, 7, None),
    ("dependency", "completed", "user-service", (5, 1, 2, 1, 1), 48, 11, None),
    ("sbom", "completed", "auth-service", (4, 1, 1, 1, 1), 60, 8, None),
    ("container", "completed", "production-cluster", (7, 2, 3, 2, 0), 72, 13, None),
    ("secret", "completed", "all-repositories", (10, 2, 5, 3, 0), 96, 6, None),
]


def _build_scans() -> list[dict]:
    scans = []
    for idx, (scan_type, status, target, findings, hours_ago, duration, reason) in enumerate(_RAW_SCANS, start=1):
        started = _BASE_TIME - timedelta(hours=hours_ago)
        completed = started + timedelta(minutes=duration) if duration else None
        total, crit, high, med, low = findings
        scans.append(
            {
                "id": f"scan-{idx:03d}",
                "scan_type": scan_type,
                "status": status,
                "target": target,
                "total_findings": total,
                "critical_findings": crit,
                "high_findings": high,
                "medium_findings": med,
                "low_findings": low,
                "started_at": started.isoformat(),
                "completed_at": completed.isoformat() if completed else None,
                "duration_minutes": duration,
                "failure_reason": reason,
                "source_state": SOURCE_STATE,
            }
        )
    return scans
DEMO_SCANS = _build_scans()


@router.get("/")
async def get_scans():
    return {
        "items": DEMO_SCANS,
        "total": len(DEMO_SCANS),
        "completed": len([s for s in DEMO_SCANS if s["status"] == "completed"]),
        "running": len([s for s in DEMO_SCANS if s["status"] == "running"]),
        "queued": len([s for s in DEMO_SCANS if s["status"] == "queued"]),
        "failed": len([s for s in DEMO_SCANS if s["status"] == "failed"]),
        "source_state": SOURCE_STATE,
        "simulated": True,
    }

@router.get("/{scan_id}")
async def get_scan(scan_id: str):
    for scan in DEMO_SCANS:
        if scan["id"] == scan_id:
            return {**scan, "simulated": True}
    return {"error": "Scan not found"}

@router.post("/trigger")
async def trigger_scan(request: dict):
    scan_type = request.get("scan_type", "dependency")
    target = request.get("target", "all")
    # A triggered scan is only queued; this build does not execute real scanners.
    return {
        "id": f"scan-{len(DEMO_SCANS) + 1:03d}",
        "scan_type": scan_type,
        "status": "queued",
        "target": target,
        "started_at": datetime.utcnow().isoformat(),
        "message": f"{scan_type} scan queued for {target} (simulated — no scanner executed)",
        "source_state": SOURCE_STATE,
        "simulated": True,
    }