from fastapi import APIRouter
from datetime import datetime, timedelta
router = APIRouter()

# Provenance marker surfaced by the UI. Attack paths are SIMULATED, derived from
# the demo asset/vulnerability fixtures, and NOT produced by a live attack-graph
# solver. This endpoint is NOT database-backed: the attack_paths table exists but
# no path-computation engine populates it, so returning stored rows would present
# fabricated fixtures as findings. Every response is tagged simulated=True.
SOURCE_STATE = "simulated"
RISK_MODEL = "Demo Risk Score"

# Each step's `risk` uses the same vocabulary the shared SeverityBadge understands
# (critical/high/medium/low/info/external). Steps form a consistent kill chain:
# internet source -> entry point -> vulnerability -> container/host -> IAM/secret
# -> data store. CVE and component references match the vulnerability catalogue.
ATTACK_PATHS = [
    {
        "id": "path-001",
        "name": "Internet → API Gateway → Log4Shell → Container → IAM → Database",
        "description": (
            "An attacker exploits CVE-2021-44228 (Log4Shell) in the public API "
            "gateway's log4j-core dependency to gain initial access, then pivots "
            "through the privileged gateway container to reach an overprivileged IAM "
            "role with full RDS access."
        ),
        "risk_score": 9.4,
        "risk_level": "critical",
        "risk_factors": [
            "Vulnerability severity (CVSS 10.0, CISA KEV)",
            "Internet-facing entry point",
            "Privileged container on the path",
            "Overprivileged IAM role",
            "Path depth (6 stages)",
            "Potential blast radius (production PII)",
        ],
        "steps": [
            {"node": "Internet", "type": "source", "risk": "external", "detail": "Public internet access"},
            {"node": "API Gateway (api-gateway-prod)", "type": "entry", "risk": "high", "detail": "Public endpoint exposed on port 443"},
            {"node": "CVE-2021-44228 (log4j-core 2.14.1)", "type": "vulnerability", "risk": "critical", "detail": "JNDI remote code execution (Log4Shell)"},
            {"node": "Container (gateway-container)", "type": "container", "risk": "high", "detail": "Privileged container with host network access"},
            {"node": "IAM Role (data-pipeline-role)", "type": "iam", "risk": "high", "detail": "Overprivileged role with full RDS access"},
            {"node": "Database (user-db-prod)", "type": "database", "risk": "critical", "detail": "Production database with sensitive PII data"},
        ],
        "blast_radius": ["Production PII records", "Authentication credentials", "Financial transactions", "Full RDS access"],
        "remediation": [
            "Update log4j-core to 2.17.1 or later",
            "Remove privileged mode from gateway-container",
            "Restrict data-pipeline-role to least privilege",
            "Enable network isolation for user-db-prod",
        ],
        "is_active": True,
        "discovered_at": (datetime(2024, 8, 1, 9, 0, 0) - timedelta(days=2)).isoformat(),
        "asset_id": "asset-api-gateway-prod",
        "vulnerability_id": "vuln-0",
        "source_state": SOURCE_STATE,
        "risk_model": RISK_MODEL,
    },
    {
        "id": "path-002",
        "name": "Internet → Web App → libwebp Overflow → Container → Secret → Storage",
        "description": (
            "A heap buffer overflow in libwebp (CVE-2023-4863) reachable from the "
            "public web application allows memory corruption. The container carries "
            "cloud provider credentials that grant access to sensitive storage "
            "buckets."
        ),
        "risk_score": 8.6,
        "risk_level": "critical",
        "risk_factors": [
            "Vulnerability severity (CVSS 8.8, CISA KEV)",
            "Internet-facing web application",
            "Exposed cloud credentials in container",
            "Potential blast radius (customer data)",
        ],
        "steps": [
            {"node": "Internet", "type": "source", "risk": "external", "detail": "Public internet access"},
            {"node": "Web App (web-app-frontend)", "type": "entry", "risk": "high", "detail": "Public web application"},
            {"node": "CVE-2023-4863 (libwebp 1.3.1)", "type": "vulnerability", "risk": "critical", "detail": "Heap buffer overflow via crafted WebP image"},
            {"node": "Container (web-container)", "type": "container", "risk": "high", "detail": "Cloud credentials mounted as environment variables"},
            {"node": "Secret (AWS_ACCESS_KEY_ID)", "type": "secret", "risk": "critical", "detail": "AWS access key exposed in container environment"},
            {"node": "Storage (audit-log-store)", "type": "storage", "risk": "high", "detail": "Storage bucket reachable with exposed key"},
        ],
        "blast_radius": ["Customer records", "Cloud credentials", "Audit log storage access"],
        "remediation": [
            "Update libwebp to 1.3.2 or later",
            "Remove mounted credentials from web-container",
            "Rotate the exposed AWS_ACCESS_KEY_ID",
            "Enforce bucket policies on audit-log-store",
        ],
        "is_active": True,
        "discovered_at": (datetime(2024, 8, 1, 9, 0, 0) - timedelta(days=5)).isoformat(),
        "asset_id": "asset-web-app-frontend",
        "vulnerability_id": "vuln-16",
        "source_state": SOURCE_STATE,
        "risk_model": RISK_MODEL,
    },
    {
        "id": "path-003",
        "name": "HTTP/2 Rapid Reset → Auth Service → Container → Database",
        "description": (
            "CVE-2023-44487 (HTTP/2 Rapid Reset) allows a denial of service and "
            "internal service reachability from auth-service, which lacks egress "
            "restriction and can pivot to the production database."
        ),
        "risk_score": 7.6,
        "risk_level": "high",
        "risk_factors": [
            "Vulnerability severity (CVSS 7.5, CISA KEV)",
            "Publicly reachable authentication service",
            "Database without network isolation",
        ],
        "steps": [
            {"node": "Internet", "type": "source", "risk": "external", "detail": "Public internet"},
            {"node": "Auth Service (auth-service)", "type": "entry", "risk": "medium", "detail": "Publicly exposed authentication endpoint"},
            {"node": "CVE-2023-44487 (x/net/http2 0.16.0)", "type": "vulnerability", "risk": "high", "detail": "HTTP/2 Rapid Reset denial of service"},
            {"node": "Container (auth-container)", "type": "container", "risk": "medium", "detail": "Unrestricted internal network access"},
            {"node": "Database (user-db-prod)", "type": "database", "risk": "high", "detail": "No network isolation"},
        ],
        "blast_radius": ["User credentials", "Session tokens", "Internal service discovery"],
        "remediation": [
            "Update golang.org/x/net to 0.17.0 or later",
            "Restrict auth-container egress traffic",
            "Apply a network firewall to user-db-prod",
        ],
        "is_active": True,
        "discovered_at": (datetime(2024, 8, 1, 9, 0, 0) - timedelta(days=7)).isoformat(),
        "asset_id": "asset-auth-service",
        "vulnerability_id": "vuln-4",
        "source_state": SOURCE_STATE,
        "risk_model": RISK_MODEL,
    },
    {
        "id": "path-004",
        "name": "Container Escape → Host Access → Cluster Compromise",
        "description": (
            "The ml-training-worker container runs privileged on the host and carries "
            "the runc Leaky Vessels escape (CVE-2024-21626). A successful escape "
            "reaches the host node and risks cluster-wide compromise."
        ),
        "risk_score": 9.1,
        "risk_level": "critical",
        "risk_factors": [
            "Privileged container with host access",
            "Container-escape vulnerability (CVE-2024-21626)",
            "Lateral movement to host and cluster",
            "Potential blast radius (cluster-wide)",
        ],
        "steps": [
            {"node": "Host Node (k8s-worker-3)", "type": "host", "risk": "high", "detail": "Runs the privileged ml-training-worker pod"},
            {"node": "Container (ml-training-worker)", "type": "entry", "risk": "critical", "detail": "Privileged container with host namespace access"},
            {"node": "CVE-2024-21626 (runc 1.1.11)", "type": "vulnerability", "risk": "critical", "detail": "Container escape via leaked working-directory file descriptor"},
            {"node": "Kubernetes Cluster", "type": "cluster", "risk": "critical", "detail": "Full cluster compromise possible"},
            {"node": "Sensitive Data", "type": "data", "risk": "critical", "detail": "All workloads and mounted secrets reachable"},
        ],
        "blast_radius": ["Cluster-wide compromise", "Cloud credentials", "All workload secrets"],
        "remediation": [
            "Update runc to 1.1.12 or later",
            "Remove privileged mode from ml-training-worker",
            "Apply a restrictive pod security policy",
            "Enable seccomp profiles for the workload",
        ],
        "is_active": True,
        "discovered_at": (datetime(2024, 8, 1, 9, 0, 0) - timedelta(days=1)).isoformat(),
        "asset_id": "asset-ml-training-worker",
        "vulnerability_id": "vuln-2",
        "source_state": SOURCE_STATE,
        "risk_model": RISK_MODEL,
    },
]
@router.get("/")
async def get_attack_paths():
    return {
        "items": ATTACK_PATHS,
        "total": len(ATTACK_PATHS),
        "critical": len([p for p in ATTACK_PATHS if p["risk_level"] == "critical"]),
        "high": len([p for p in ATTACK_PATHS if p["risk_level"] == "high"]),
        "source_state": SOURCE_STATE,
        "simulated": True,
        "risk_model": RISK_MODEL,
    }

@router.get("/stats/overview")
async def get_attack_path_stats():
    return {
        "total_paths": len(ATTACK_PATHS),
        "critical": len([p for p in ATTACK_PATHS if p["risk_level"] == "critical"]),
        "high": len([p for p in ATTACK_PATHS if p["risk_level"] == "high"]),
        "avg_risk_score": round(sum(p["risk_score"] for p in ATTACK_PATHS) / len(ATTACK_PATHS), 1),
        "source_state": SOURCE_STATE,
        "simulated": True,
        "risk_model": RISK_MODEL,
    }

@router.get("/{path_id}")
async def get_attack_path(path_id: str):
    for path in ATTACK_PATHS:
        if path["id"] == path_id:
            return {**path, "simulated": True}
    return {"error": "Attack path not found"}