"""Frontend-compatibility tests for empty and populated API responses.

The UI reads specific keys off these payloads (see frontend/src/lib/api.ts and the
pages). These tests pin the contract so an empty database cannot produce a
response shape that breaks rendering.
"""

from __future__ import annotations

import pytest

from tests.conftest import make_asset, make_vulnerability

pytestmark = pytest.mark.anyio

# Keys the frontend dereferences directly (vulns?.items, vulns?.total, ...).
VULN_LIST_KEYS = {"items", "total", "page", "page_size", "total_pages", "source_state", "summary"}
ASSET_LIST_KEYS = {
    "items",
    "total",
    "page",
    "page_size",
    "total_pages",
    "publicly_exposed",
    "source_state",
}
VULN_ITEM_KEYS = {
    "id",
    "cve_id",
    "title",
    "severity",
    "cvss_score",
    "affected_component",
    "fixed_version",
    "status",
    "asset_name",
    "cisa_kev",
    "publicly_exposed",
}
ASSET_ITEM_KEYS = {
    "id",
    "name",
    "asset_type",
    "publicly_exposed",
    "criticality",
    "vulnerability_count",
}


async def test_empty_vulnerability_payload_shape(client):
    body = (await client.get("/api/v1/vulnerabilities/")).json()
    assert VULN_LIST_KEYS.issubset(body.keys())
    assert isinstance(body["items"], list)
    assert isinstance(body["total"], int)
    # The page guards on `vulns?.items ?? []`, so items must always be a list.
    assert body["items"] == []


async def test_empty_asset_payload_shape(client):
    body = (await client.get("/api/v1/assets/")).json()
    assert ASSET_LIST_KEYS.issubset(body.keys())
    assert body["items"] == []


async def test_populated_items_have_fields_the_ui_reads(client, session_factory):
    async with session_factory() as s:
        asset = make_asset(name="api", publicly_exposed=True)
        s.add(asset)
        await s.flush()
        s.add(make_vulnerability(title="finding", asset_id=asset.id))
        await s.commit()

    vuln_item = (await client.get("/api/v1/vulnerabilities/")).json()["items"][0]
    assert VULN_ITEM_KEYS.issubset(vuln_item.keys())
    # cve_id is rendered with `.toLowerCase()` in the search filter, so it must
    # never be null in the payload for a row that has one.
    assert isinstance(vuln_item["cve_id"], str)

    asset_item = (await client.get("/api/v1/assets/")).json()["items"][0]
    assert ASSET_ITEM_KEYS.issubset(asset_item.keys())


async def test_dashboard_payload_shape_for_empty_db(client):
    summary = (await client.get("/api/v1/dashboard/summary")).json()
    for key in (
        "total_assets",
        "publicly_exposed",
        "total_vulnerabilities",
        "critical",
        "high",
        "active_attack_paths",
        "secrets_detected",
        "containers",
        "recent_findings",
        "risk_categories",
        "system_health",
        "attack_surface",
    ):
        assert key in summary
    assert isinstance(summary["recent_findings"], list)
    assert isinstance(summary["risk_categories"], list)
    assert "status" in summary["system_health"]

    score = (await client.get("/api/v1/dashboard/security-score")).json()
    for key in ("overall_score", "asset_coverage", "vulnerability_score", "exposure_score"):
        assert key in score
    assert isinstance(score["trend"], list)
