from fastapi import APIRouter
from datetime import datetime, timedelta
from app.api._demo_data import DEMO_CONTAINERS, VULNERABILITY_CATALOG, cvss_to_severity
router = APIRouter()

# Provenance marker surfaced by the UI. Repositories, SBOMs and dependency lists
# are SIMULATED; they are not the result of live GitHub/SCM scanning.
SOURCE_STATE = "simulated"

ScanTime = datetime(2024, 8, 1, 9, 0, 0)

# Repository inventory. Findings counts are derived from the dependency list so
# the repository summary and its dependency details cannot contradict each other.
_CATALOGUE_BY_COMPONENT = {v["affected_component"]: v for v in VULNERABILITY_CATALOG}

_REPO_DEFS = [
    ("repo-api-gateway", "api-gateway", "Go", ["log4j-core", "golang.org/x/net/http2"]),
    ("repo-payment-service", "payment-service", "Java", ["spring-webmvc", "postgresql-jdbc"]),
    ("repo-web-app", "web-app", "TypeScript", ["node", "libwebp"]),
    ("repo-user-service", "user-service", "Python", ["postgresql-jdbc"]),
    ("repo-data-pipeline", "data-pipeline", "Python", []),
    ("repo-auth-service", "auth-service", "Go", ["golang.org/x/net/http2"]),
    ("repo-notification-service", "notification-service", "Node", ["node"]),
    ("repo-ml-training", "ml-training", "Python", []),
    ("repo-infrastructure", "infrastructure", "HCL", []),
    ("repo-security-scanner", "security-scanner", "Rust", []),
    ("repo-cli-tool", "cli-tool", "Go", []),
]


def _build_repos() -> list[dict]:
    repos = []
    for idx, (rid, name, lang, components) in enumerate(_REPO_DEFS):
        findings = [_CATALOGUE_BY_COMPONENT[c] for c in components if c in _CATALOGUE_BY_COMPONENT]
        by_sev = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            by_sev[cvss_to_severity(f["cvss_score"])] += 1
        # Security posture (0-100, higher is better) is derived from the finding
        # mix. It is a DEMO posture score, not a validated risk model.
        posture = max(0, 100 - (by_sev["critical"] * 25 + by_sev["high"] * 12 + by_sev["medium"] * 5))
        repos.append(
            {
                "id": rid,
                "name": name,
                "url": f"https://github.com/example-org/{name}",
                "language": lang,
                "default_branch": "main",
                "security_score": posture,
                "total_findings": len(findings),
                "critical_findings": by_sev["critical"],
                "high_findings": by_sev["high"],
                "medium_findings": by_sev["medium"],
                "low_findings": by_sev["low"],
                "dependencies": max(20, 60 + idx * 34),
                "secrets_detected": 2 if name in ("payment-service", "auth-service", "api-gateway") else 0,
                "last_scan": (ScanTime - timedelta(hours=idx * 5)).isoformat(),
                "last_commit": (ScanTime - timedelta(hours=idx * 9)).isoformat(),
                "ci_cd_pipeline": "github-actions" if idx % 2 == 0 else "gitlab-ci",
                "ci_cd_gate": "passing" if posture >= 70 else "failing",
                "source_state": SOURCE_STATE,
            }
        )
    return repos
DEMO_REPOSITORIES = _build_repos()
_REPO_BY_ID = {r["id"]: r for r in DEMO_REPOSITORIES}

@router.get("/repositories")
async def get_repositories():
    return {"items": DEMO_REPOSITORIES, "total": len(DEMO_REPOSITORIES), "source_state": SOURCE_STATE}

# Static SBOM/dependency catalogue keyed by component. Versions match the
# vulnerability catalogue so an entry flagged vulnerable always has a CVE.
_DEPENDENCY_ROWS = [
    {"name": "log4j-core", "installed_version": "2.14.1"},
    {"name": "golang.org/x/net/http2", "installed_version": "0.16.0"},
    {"name": "spring-webmvc", "installed_version": "5.3.17"},
    {"name": "postgresql-jdbc", "installed_version": "42.6.0"},
    {"name": "libwebp", "installed_version": "1.3.1"},
    {"name": "node", "installed_version": "20.11.0"},
    {"name": "axios", "installed_version": "1.6.2"},
    {"name": "react-dom", "installed_version": "18.2.0"},
]

@router.get("/repositories/{repo_id}/dependencies")
async def get_repository_dependencies(repo_id: str):
    repo = _REPO_BY_ID.get(repo_id)
    if not repo:
        return {"error": "Repository not found"}

    rows = []
    for row in _DEPENDENCY_ROWS:
        vuln = _CATALOGUE_BY_COMPONENT.get(row["name"])
        if vuln is None:
            rows.append({**row, "latest_version": row["installed_version"], "vulnerable": False})
            continue
        rows.append(
            {
                "name": row["name"],
                "installed_version": row["installed_version"],
                "latest_version": vuln["fixed_version"],
                "vulnerable": True,
                "severity": cvss_to_severity(vuln["cvss_score"]),
                "cve": vuln["cve_id"],
                "cisa_kev": vuln["cisa_kev"],
                "fixed_version": vuln["fixed_version"],
            }
        )

    vulnerable = [r for r in rows if r["vulnerable"]]
    return {
        "items": rows,
        "total": repo["dependencies"],
        "vulnerable": len(vulnerable),
        "source_state": SOURCE_STATE,
    }

@router.get("/repositories/{repo_id}/secrets")
async def get_repository_secrets(repo_id: str):
    # Secret detections are shared with the Secrets page inventory but reported
    # per repository. Values are always masked placeholders.
    all_secrets = [
        {"name": "AWS_ACCESS_KEY_ID", "type": "api_key", "severity": "critical", "location": "services/payment/.env", "repository": "payment-service", "exposed": True, "rotated": False},
        {"name": "JWT_SIGNING_SECRET", "type": "token", "severity": "critical", "location": "config/auth.js", "repository": "auth-service", "exposed": True, "rotated": True},
        {"name": "GITHUB_TOKEN", "type": "token", "severity": "high", "location": ".github/workflows/deploy.yml", "repository": "api-gateway", "exposed": True, "rotated": True},
    ]
    repo = _REPO_BY_ID.get(repo_id)
    repo_name = repo["name"] if repo else None
    items = [
        {**s, "value": "[Protected Secret]", "source_state": SOURCE_STATE}
        for s in all_secrets
        if s["repository"] == repo_name
    ]
    return {"items": items, "total": len(items), "source_state": SOURCE_STATE}

@router.get("/repositories/{repo_id}/sbom")
async def get_repository_sbom(repo_id: str):
    packages = [
        {
            "name": r["name"],
            "version": r["installed_version"],
            "license": "Apache-2.0" if "log4j" in r["name"] else "MIT",
            "supplier": "upstream",
        }
        for r in _DEPENDENCY_ROWS
    ]
    repo = _REPO_BY_ID.get(repo_id)
    return {
        "spec_version": "SPDX-2.3",
        "data_license": "CC0-1.0",
        "packages": packages,
        "total_packages": repo["dependencies"] if repo else len(packages),
        "generated_at": ScanTime.isoformat(),
        "source_state": SOURCE_STATE,
    }

@router.get("/containers")
async def get_containers():
    items = [{**c, "source_state": SOURCE_STATE} for c in DEMO_CONTAINERS]
    return {
        "items": items,
        "total": len(items),
        "privileged": len([c for c in DEMO_CONTAINERS if c["privileges"] == "privileged"]),
        "running": len([c for c in DEMO_CONTAINERS if c["status"] == "running"]),
        "exposed_ports": sum(len(c["exposed_ports"]) for c in DEMO_CONTAINERS),
        "source_state": SOURCE_STATE,
    }

@router.get("/ci-cd")
async def get_ci_cd_pipelines():
    # Derived from the same repository posture so the CI/CD gate and the
    # repository score stay consistent.
    items = [
        {
            "name": r["name"],
            "status": r["ci_cd_gate"],
            "security_gates": True,
            "last_build": r["ci_cd_gate"],
            "source_state": SOURCE_STATE,
        }
        for r in DEMO_REPOSITORIES
        if r["name"] in ("api-gateway", "payment-service", "auth-service")
    ]
    return {"items": items, "total": len(items), "source_state": SOURCE_STATE}