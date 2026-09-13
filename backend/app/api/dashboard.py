from fastapi import APIRouter
import random
from datetime import datetime, timedelta
from app.api._demo_data import DEMO_ASSETS, DEMO_CONTAINERS
from app.api.vulnerabilities import DEMO_VULNERABILITIES
from app.api.attack_paths import ATTACK_PATHS
router = APIRouter()

# Provenance marker surfaced by the UI. All dashboard aggregates are SIMULATED
# and computed from the shared demo fixtures so cross-page numbers agree.
SOURCE_STATE = "simulated"

# Deterministic trend series (fixed seed) so the sparkline does not jitter on
# every refresh and is clearly a demonstration series.
_trend_rng = random.Random(1337)
DEMO_SECURITY_SCORE = {
    "overall_score": 72.4,
    "asset_coverage": 85.0,
    "vulnerability_score": 65.0,
    "exposure_score": 78.0,
    "iam_score": 82.0,
    "secret_score": 70.0,
    "trend": [
        {
            "date": (datetime(2024, 8, 1) - timedelta(days=i)).date().isoformat(),
            "score": round(70 + _trend_rng.uniform(-4, 7), 1),
        }
        for i in range(14, -1, -1)
    ],
    "updated_at": datetime(2024, 8, 1, 9, 0, 0).isoformat(),
    "source_state": SOURCE_STATE,
    "model": "Demo Security Score",
}


def _counts_by_severity() -> dict[str, int]:
    # Open (unresolved) findings only, so the dashboard does not inflate
    # outstanding risk with already-fixed vulnerabilities.
    open_vulns = [v for v in DEMO_VULNERABILITIES if v["status"] != "fixed"]
    return {
        "critical": len([v for v in open_vulns if v["severity"] == "critical"]),
        "high": len([v for v in open_vulns if v["severity"] == "high"]),
        "medium": len([v for v in open_vulns if v["severity"] == "medium"]),
        "low": len([v for v in open_vulns if v["severity"] == "low"]),
    }

@router.get("/security-score")
async def get_security_score():
    return DEMO_SECURITY_SCORE
@router.get("/summary")
async def get_dashboard_summary():
    sev = _counts_by_severity()
    critical_kev = [v for v in DEMO_VULNERABILITIES if v["cisa_kev"]]
    exposed_assets = [a for a in DEMO_ASSETS if a["publicly_exposed"]]

    recent_findings = [
        {
            "id": "finding-001",
            "title": "CVE-2021-44228 (log4j-core 2.14.1): remote code execution on api-gateway-prod",
            "severity": "critical",
            "source": "Dependency Scan",
            "asset": "api-gateway-prod",
            "discovered_at": datetime(2024, 8, 1, 9, 0, 0).isoformat(),
            "status": "active",
        },
        {
            "id": "finding-002",
            "title": "IAM role 'data-pipeline-role' has an overly permissive trust policy",
            "severity": "critical",
            "source": "IAM Analysis",
            "asset": "data-pipeline-role",
            "discovered_at": datetime(2024, 8, 1, 6, 30, 0).isoformat(),
            "status": "active",
        },
        {
            "id": "finding-003",
            "title": "AWS_ACCESS_KEY_ID exposed in repository 'payment-service/.env'",
            "severity": "critical",
            "source": "Secret Detection",
            "asset": "payment-service",
            "discovered_at": datetime(2024, 8, 1, 3, 15, 0).isoformat(),
            "status": "active",
        },
        {
            "id": "finding-004",
            "title": "Container 'ml-training-worker' running in privileged mode on k8s-worker-3",
            "severity": "high",
            "source": "Container Scan",
            "asset": "ml-training-worker",
            "discovered_at": datetime(2024, 7, 31, 20, 45, 0).isoformat(),
            "status": "in_triage",
        },
        {
            "id": "finding-005",
            "title": "Database 'user-db-prod' reachable from a public network range",
            "severity": "critical",
            "source": "Network Analysis",
            "asset": "user-db-prod",
            "discovered_at": datetime(2024, 7, 31, 14, 5, 0).isoformat(),
            "status": "active",
        },
    ]

    return {
        "total_assets": len(DEMO_ASSETS),
        "publicly_exposed": len(exposed_assets),
        "total_vulnerabilities": len(DEMO_VULNERABILITIES),
        "critical": sev["critical"],
        "high": sev["high"],
        "medium": sev["medium"],
        "low": sev["low"],
        "cisa_kev": len(critical_kev),
        "active_attack_paths": len([p for p in ATTACK_PATHS if p["is_active"]]),
        "containers": len(DEMO_CONTAINERS),
        "privileged_containers": len([c for c in DEMO_CONTAINERS if c["privileges"] == "privileged"]),
        "secrets_detected": 10,
        "secrets_rotation_required": 4,
        "iam_roles": 32,
        "databases": len([a for a in DEMO_ASSETS if a["asset_type"] == "database"]),
        "repositories": 11,
        "recent_findings": recent_findings,
        "risk_categories": [
            {"category": "Vulnerability Management", "score": 65, "status": "at_risk"},
            {"category": "Identity & Access", "score": 82, "status": "needs_attention"},
            {"category": "Data Security", "score": 74, "status": "needs_attention"},
            {"category": "Network Security", "score": 88, "status": "good"},
            {"category": "Container Security", "score": 71, "status": "needs_attention"},
            {"category": "Secret Management", "score": 70, "status": "needs_attention"},
            {"category": "Supply Chain", "score": 76, "status": "needs_attention"},
            {"category": "Compliance", "score": 80, "status": "good"},
        ],
        "system_health": {
            "status": "synced",
            "last_sync": datetime(2024, 8, 1, 8, 57, 0).isoformat(),
            "scanners_active": 4,
            "queued_scans": 2,
            "uptime": "14d 7h 32m",
        },
        "attack_surface": {
            "total_exposed": len(exposed_assets),
            "api_endpoints": len([a for a in DEMO_ASSETS if a["asset_type"] == "api_endpoint"]),
            "web_applications": 3,
            "open_ports": 18,
            "dns_records": 7,
            "cloud_instances": len([a for a in DEMO_ASSETS if a["asset_type"] == "cloud_instance"]),
        },
        "source_state": SOURCE_STATE,
    }