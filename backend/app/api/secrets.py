from fastapi import APIRouter
from datetime import datetime
router = APIRouter()

# Provenance marker surfaced by the UI: these are SIMULATED detections, not the
# output of a live secret scanner. Secret values are never stored or returned —
# only a masked placeholder identifier. This endpoint is NOT database-backed: the
# secrets table would only hold real detections from a scanner that is not
# connected, so it is left empty rather than seeded with fabricated secrets.
SOURCE_STATE = "simulated"
MASKED_VALUE = "[Protected Secret]"

# Deterministic fixture (no random.*) so the exposure/rotation model is stable.
# `exposed` describes whether the value was found outside a secret manager;
# `rotated` describes whether the simulated remediation step was completed.
_SECRETS = [
    {
        "id": "secret-1",
        "name": "AWS_ACCESS_KEY_ID",
        "type": "api_key",
        "provider": "aws",
        "severity": "critical",
        "location": "services/payment/.env",
        "repository": "payment-service",
        "exposed": True,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 20, 14, 12, 0),
    },
    {
        "id": "secret-2",
        "name": "JWT_SIGNING_SECRET",
        "type": "token",
        "provider": "internal",
        "severity": "critical",
        "location": "config/auth.js",
        "repository": "auth-service",
        "exposed": True,
        "rotated": True,
        "discovered_at": datetime(2024, 7, 18, 9, 40, 0),
    },
    {
        "id": "secret-3",
        "name": "DATABASE_URL",
        "type": "connection_string",
        "provider": "postgres",
        "severity": "critical",
        "location": "deploy/.env.example",
        "repository": "user-service",
        "exposed": True,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 22, 16, 5, 0),
    },
    {
        "id": "secret-4",
        "name": "GITHUB_TOKEN",
        "type": "token",
        "provider": "github",
        "severity": "high",
        "location": ".github/workflows/deploy.yml",
        "repository": "api-gateway",
        "exposed": True,
        "rotated": True,
        "discovered_at": datetime(2024, 7, 15, 11, 22, 0),
    },
    {
        "id": "secret-5",
        "name": "STRIPE_SECRET_KEY",
        "type": "api_key",
        "provider": "stripe",
        "severity": "high",
        "location": "services/billing/config.py",
        "repository": "payment-service",
        "exposed": False,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 25, 8, 55, 0),
    },
    {
        "id": "secret-6",
        "name": "DOCKER_PASSWORD",
        "type": "password",
        "provider": "docker",
        "severity": "high",
        "location": "deploy/settings.sh",
        "repository": "infrastructure",
        "exposed": True,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 12, 19, 30, 0),
    },
    {
        "id": "secret-7",
        "name": "REDIS_PASSWORD",
        "type": "password",
        "provider": "redis",
        "severity": "high",
        "location": "docker-compose.yml",
        "repository": "infrastructure",
        "exposed": True,
        "rotated": True,
        "discovered_at": datetime(2024, 7, 10, 13, 10, 0),
    },
    {
        "id": "secret-8",
        "name": "SENTRY_DSN",
        "type": "token",
        "provider": "sentry",
        "severity": "medium",
        "location": "config/app.js",
        "repository": "web-app",
        "exposed": False,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 28, 10, 0, 0),
    },
    {
        "id": "secret-9",
        "name": "SLACK_WEBHOOK_URL",
        "type": "token",
        "provider": "slack",
        "severity": "medium",
        "location": "monitoring/alerts.py",
        "repository": "security-scanner",
        "exposed": False,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 29, 15, 45, 0),
    },
    {
        "id": "secret-10",
        "name": "DATADOG_API_KEY",
        "type": "api_key",
        "provider": "datadog",
        "severity": "medium",
        "location": "monitoring/config.yml",
        "repository": "infrastructure",
        "exposed": False,
        "rotated": False,
        "discovered_at": datetime(2024, 7, 30, 7, 20, 0),
    },
]


def _lifecycle(secret: dict) -> dict:
    # Derive the remediation lifecycle for a secret. Only states the fixture can
    # actually support are produced: a secret that was never exposed is
    # 'detected'; an exposed secret is either awaiting rotation or has been
    # rotated (verification pending, since no verification step exists here).
    if not secret["exposed"]:
        return {
            "state": "detected",
            "label": "Not Exposed",
            "rotation_required": False,
            "exposure_confirmed": False,
            "verification": "n/a",
        }
    if secret["rotated"]:
        return {
            "state": "rotated",
            "label": "Rotated",
            "rotation_required": False,
            "exposure_confirmed": True,
            "verification": "Verification pending",
        }
    return {
        "state": "rotation_required",
        "label": "Rotation Required",
        "rotation_required": True,
        "exposure_confirmed": True,
        "verification": "Not verified",
    }


def _serialize(secret: dict) -> dict:
    return {
        **{k: v for k, v in secret.items() if k != "discovered_at"},
        "discovered_at": secret["discovered_at"].isoformat(),
        "value": MASKED_VALUE,
        "source_state": SOURCE_STATE,
        "source_file": secret["location"],
        "lifecycle": _lifecycle(secret),
    }

@router.get("/")
async def get_secrets():
    items = [_serialize(s) for s in _SECRETS]
    return {
        "items": items,
        "total": len(items),
        "exposed": len([s for s in items if s["exposed"]]),
        "rotated": len([s for s in items if s["rotated"]]),
        "rotation_required": len([s for s in items if s["lifecycle"]["rotation_required"]]),
        "not_exposed": len([s for s in items if not s["exposed"]]),
        "source_state": SOURCE_STATE,
        "simulated": True,
    }

@router.get("/{secret_id}")
async def get_secret(secret_id: str):
    for secret in _SECRETS:
        if secret["id"] == secret_id:
            return {**_serialize(secret), "simulated": True}
    return {"error": "Secret not found"}