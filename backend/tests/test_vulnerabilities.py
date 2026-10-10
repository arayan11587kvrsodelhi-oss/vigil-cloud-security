"""Vulnerability endpoint tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.core.database import get_db
from app.main import app as fastapi_app
from tests.conftest import make_asset, make_vulnerability

pytestmark = pytest.mark.anyio


async def test_empty_vulnerability_table_returns_empty_collection(client):
    body = (await client.get("/api/v1/vulnerabilities/")).json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["source_state"] == "database"
    summary = body["summary"]
    for key in ("total", "critical", "high", "medium", "low", "cisa_kev", "remediation_required"):
        assert summary[key] == 0


async def test_vulnerability_list_is_database_backed(client, session_factory):
    async with session_factory() as s:
        s.add(make_vulnerability(title="Log4Shell", severity="critical", cve_id="CVE-2021-44228"))
        s.add(make_vulnerability(title="Spring4Shell", severity="high", cve_id="CVE-2022-22965"))
        await s.commit()

    body = (await client.get("/api/v1/vulnerabilities/")).json()
    assert body["total"] == 2
    assert {v["cve_id"] for v in body["items"]} == {"CVE-2021-44228", "CVE-2022-22965"}


async def test_vulnerability_summary_counts_only_open_findings(client, session_factory):
    async with session_factory() as s:
        s.add(make_vulnerability(title="open-crit", severity="critical", status="active"))
        s.add(make_vulnerability(title="triage-high", severity="high", status="in_triage"))
        s.add(make_vulnerability(title="fixed-crit", severity="critical", status="fixed"))
        s.add(make_vulnerability(title="kev", severity="high", status="active", cisa_kev=True))
        await s.commit()

    summary = (await client.get("/api/v1/vulnerabilities/stats/overview")).json()
    assert summary["total"] == 4
    assert summary["critical"] == 1  # fixed critical excluded from open counts
    assert summary["high"] == 2
    assert summary["remediation_required"] == 3  # active + in_triage
    assert summary["fixed"] == 1
    assert summary["cisa_kev"] == 1


async def test_vulnerability_filtering(client, session_factory):
    async with session_factory() as s:
        s.add(make_vulnerability(title="a", severity="critical", status="active", cve_id="CVE-2024-1111"))
        s.add(make_vulnerability(title="b", severity="low", status="fixed", cve_id="CVE-2024-2222"))
        await s.commit()

    sev = (await client.get("/api/v1/vulnerabilities/", params={"severity": "critical"})).json()
    assert sev["total"] == 1
    assert sev["items"][0]["severity"] == "critical"

    st = (await client.get("/api/v1/vulnerabilities/", params={"status": "fixed"})).json()
    assert st["total"] == 1
    assert st["items"][0]["status"] == "fixed"

    srch = (await client.get("/api/v1/vulnerabilities/", params={"search": "2222"})).json()
    assert srch["total"] == 1
    assert srch["items"][0]["cve_id"] == "CVE-2024-2222"


async def test_vulnerability_pagination_metadata(client, session_factory):
    async with session_factory() as s:
        for i in range(45):
            s.add(
                make_vulnerability(
                    title=f"v{i:03d}",
                    discovered_at=datetime(2024, 8, 1) - timedelta(hours=i),
                )
            )
        await s.commit()

    body = (await client.get("/api/v1/vulnerabilities/", params={"page": 2, "page_size": 20})).json()
    assert body["total"] == 45
    assert body["page"] == 2
    assert body["page_size"] == 20  # echoed, not the row count
    assert body["total_pages"] == 3
    assert len(body["items"]) == 20


async def test_vulnerability_detail_includes_asset_name(client, session_factory):
    async with session_factory() as s:
        asset = make_asset(name="api-gateway-prod", publicly_exposed=True)
        s.add(asset)
        await s.flush()
        vuln = make_vulnerability(title="Log4Shell", asset_id=asset.id)
        s.add(vuln)
        await s.commit()
        vuln_id = str(vuln.id)

    detail = (await client.get(f"/api/v1/vulnerabilities/{vuln_id}")).json()
    assert detail["asset_name"] == "api-gateway-prod"
    assert detail["publicly_exposed"] is True
    assert detail["id"] == vuln_id


async def test_vulnerability_detail_missing_returns_404(client):
    resp = await client.get(f"/api/v1/vulnerabilities/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_vulnerability_detail_invalid_uuid_returns_404(client):
    assert (await client.get("/api/v1/vulnerabilities/nope")).status_code == 404


async def test_database_failure_not_disguised_as_demo(client):
    from sqlalchemy.exc import OperationalError

    async def _broken_db():
        class _Session:
            async def execute(self, *a, **k):
                raise OperationalError("SELECT 1", {}, Exception("down"))

            async def scalar(self, *a, **k):
                raise OperationalError("SELECT 1", {}, Exception("down"))

        yield _Session()

    fastapi_app.dependency_overrides[get_db] = _broken_db
    resp = await client.get("/api/v1/vulnerabilities/")
    assert resp.status_code == 500
    assert "simulated" not in resp.text.lower()
