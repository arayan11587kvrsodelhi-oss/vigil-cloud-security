from fastapi import APIRouter
router = APIRouter()

# Provenance marker surfaced by the UI. These responses are STATIC, SIMULATED
# analysis authored for the demo. No external intelligence source, LLM, or live
# feed is consulted. Any statement about threat groups, campaigns or trends is
# explicitly demo context, not live intelligence.
SOURCE_STATE = "simulated"
ANALYSIS_MODEL = "Demo Analyst (static)"
THREAT_CONTEXT_LABEL = "Simulated Intelligence — not sourced from a live feed"

# Structured analyst output. Each entry follows Finding -> Evidence -> Risk ->
# Impact -> Recommended action so the page reads like a triage note rather than
# prose.
AI_RESPONSES = {
    "vulnerability": {
        "finding": "CVE-2021-44228 (Log4Shell) affects log4j-core 2.14.1 on api-gateway-prod.",
        "evidence": [
            "log4j-core 2.14.1 installed on api-gateway-prod; fixed version is 2.17.1.",
            "CVSS v3 base score 10.0 (AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H).",
            "Flagged CISA KEV in this demo dataset; a public exploit is marked available.",
            "api-gateway-prod is internet-facing in the demo asset inventory.",
        ],
        "risk": "Critical. The package enables JNDI-driven remote code execution when attacker-controlled strings reach log messages, and the affected service is publicly exposed.",
        "impact": "Potential remote code execution on a production API gateway, with follow-on access to the IAM role and database described in attack path-001.",
        "recommended_actions": [
            "Update log4j-core to 2.17.1 or later and redeploy api-gateway-prod.",
            "Search for other components on the same host that still bundle log4j-core.",
            "Confirm no JNDI lookups are reachable from untrusted input as a temporary mitigation.",
        ],
        "threat_context": (
            THREAT_CONTEXT_LABEL + ". Log4Shell is a widely documented vulnerability; "
            "no specific actor, campaign or live exploitation statistic is claimed in this demo."
        ),
        "source_state": SOURCE_STATE,
        "model": ANALYSIS_MODEL,
    },
    "attack_path": {
        "finding": "Attack path-001 reaches user-db-prod from the internet through api-gateway-prod.",
        "evidence": [
            "6-stage chain: Internet -> api-gateway-prod -> CVE-2021-44228 -> gateway-container -> data-pipeline-role -> user-db-prod.",
            "Entry point (api-gateway-prod) is internet-facing in the demo inventory.",
            "gateway-container runs privileged with host network access.",
            "Intermediate IAM role is modelled as overprivileged with full RDS access.",
        ],
        "risk": "Critical (demo risk score 9.4). Every step in the chain is present simultaneously in the demo data.",
        "impact": "A single exploited dependency could yield database access to production PII. Blast radius spans PII records, credentials and financial transactions.",
        "recommended_actions": [
            "Patch log4j-core on api-gateway-prod first (breaks the chain at step 3).",
            "Remove privileged mode from gateway-container.",
            "Apply least privilege to data-pipeline-role.",
            "Add network isolation to user-db-prod.",
        ],
        "threat_context": (
            THREAT_CONTEXT_LABEL + ". The chain is a plausible cloud lateral-movement "
            "pattern; no specific adversary is attributed."
        ),
        "source_state": SOURCE_STATE,
        "model": ANALYSIS_MODEL,
    },
    "general": {
        "finding": "Security posture is mixed: vulnerability management and secret rotation need the most attention.",
        "evidence": [
            "Vulnerability Management 65/100 and Secret Management 70/100 are the lowest posture categories.",
            "Real exploits plus CISA KEV flags co-occur on the internet-facing API gateway.",
            "Two containers run privileged in the demo inventory.",
            "4 detected secrets are exposed and still marked rotation-required.",
        ],
        "risk": "Elevated. Exposure and unrotated secrets compound the exploitability of known CVEs.",
        "impact": "Highest impact is concentrated on api-gateway-prod and user-db-prod, which both appear on active attack paths.",
        "recommended_actions": [
            "Prioritise patch of internet-facing, KEV-flagged CVEs.",
            "Rotate the 4 exposed secrets and verify rotation.",
            "Remove privileged mode from gateway-container and ml-training-worker.",
            "Review the data-pipeline-role IAM policy.",
        ],
        "threat_context": (
            THREAT_CONTEXT_LABEL + ". No percentage increases, named threat groups or "
            "active campaign claims are made in this demo."
        ),
        "source_state": SOURCE_STATE,
        "model": ANALYSIS_MODEL,
    },
}

@router.post("/analyze")
async def ai_analyze(request: dict):
    query_type = request.get("context", "general")
    return AI_RESPONSES.get(query_type, AI_RESPONSES["general"])

@router.post("/explain-vulnerability")
async def ai_explain_vulnerability(request: dict):
    base = AI_RESPONSES["vulnerability"]
    return {
        **base,
        "cve_id": request.get("cve_id", ""),
        "summary": base["finding"],
        "risk_assessment": base["risk"],
    }

@router.post("/explain-attack-path")
async def ai_explain_attack_path(request: dict):
    base = AI_RESPONSES["attack_path"]
    return {
        **base,
        "path_id": request.get("path_id", ""),
        "summary": base["finding"],
        "risk_assessment": base["risk"],
    }