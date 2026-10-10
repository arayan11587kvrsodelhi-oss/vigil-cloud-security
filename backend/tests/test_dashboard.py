"""Dashboard summary and security-score consistency with the DB-backed pages."""

from __future__ import annotations

import uuid

import pytest

from tests.conftest import make_asset, make_container, make_vulnerability

pytestmark = pytest.mark.anyio


async def test_empty_dashboard_returns_zero_totals(client):
    body = (await client.get("/api/v1/dashboard/summary")).json()
    assert body["total_assets"] == 0
    assert body["total_vulnerabilities"] == 0
    assert body["critical"] == 0
    assert body["publicly_exposed"] == 0
    assert body["recent_findings"] == []
    assert body["source_state"] == "database"


async def test_dashboard_summary_matches_assets_and_vulnerabilities_pages(client, session_factory):
    """The dashboard numbers must agree with the assets/vulnerabilities endpoints."""
    async with session_factory() as s:
        a1 = make_asset(name="exposed", publicly_exposed=True)
        a2 = make_asset(name="internal")
        s.add_all([a1, a2])
        await s.flush()
        s.add(make_vulnerability(title="c1", severity="critical", status="active", asset_id=a1.id))
        s.add(make_vulnerability(title="h1", severity="high", status="in_triage", asset_id=a1.id))
        s.add(make_vulnerability(title="h2", severity="high", status="fixed", asset_id=a2.id))
        s.add(make_container(name="c", privileges="privileged"))
        await s.commit()

    summary = (await client.get("/api/v1/dashboard/summary")).json()
    assets = (await client.get("/api/v1/assets/")).json()
    vulns = (await client.get("/api/v1/vulnerabilities/")).json()

    assert summary["total_assets"] == assets["total"] == 2
    assert summary["publicly_exposed"] == assets["publicly_exposed"] == 1
    assert summary["total_vulnerabilities"] == vulns["total"] == 3
    # Open-severity counts agree across dashboard and vulnerabilities summary.
    assert summary["critical"] == vulns["summary"]["critical"]
    assert summary["high"] == vulns["summary"]["high"]
    assert summary["privileged_containers"] == 1


async def test_dashboard_recent_findings_are_real_records(client, session_factory):
    async with session_factory() as s:
        asset = make_asset(name="api-gateway-prod")
        s.add(asset)
        await s.flush()
        s.add(make_vulnerability(title="Log4Shell", severity="critical", asset_id=asset.id))
        await s.commit()

    body = (await client.get("/api/v1/dashboard/summary")).json()
    assert len(body["recent_findings"]) == 1
    finding = body["recent_findings"][0]
    assert finding["title"] == "Log4Shell"
    assert finding["asset"] == "api-gateway-prod"
    # Asset names must be real UUIDs resolvable via the assets endpoint.
    uuid.UUID(finding["id"])


async def test_security_score_is_db_derived_and_empty_safe(client, session_factory):
    empty = (await client.get("/api/v1/dashboard/security-score")).json()
    assert empty["source_state"] == "database"
    assert empty["asset_coverage"] == 0.0
    # No data must not present a confident perfect score.
    assert empty["overall_score"] < 100

    async with session_factory() as s:
        a = make_asset(name="x", publicly_exposed=False)
        s.add(a)
        await s.flush()
        s.add(make_vulnerability(title="v", severity="high", status="active", asset_id=a.id))
        await s.commit()

    scored = (await client.get("/api/v1/dashboard/security-score")).json()
    assert scored["asset_coverage"] == 100.0
    assert scored["overall_score"] != empty["overall_score"]
    # IAM/secret components are honestly reported as unmeasured, not invented.
    assert "iam_score" in scored["components_unavailable"]
    assert scored["iam_score"] == 0.0
