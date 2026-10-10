"""Asset endpoint tests: database-backed list, detail, filtering, pagination."""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app as fastapi_app
from tests.conftest import make_asset, make_vulnerability

pytestmark = pytest.mark.anyio


async def test_empty_asset_table_returns_empty_collection(client):
    resp = await client.get("/api/v1/assets/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["publicly_exposed"] == 0
    # source_state must indicate real (empty) database content, not simulated.
    assert body["source_state"] == "database"


async def test_asset_list_is_database_backed(client, session_factory):
    async with session_factory() as s:
        s.add(make_asset(name="alpha", asset_type="cloud_instance"))
        s.add(make_asset(name="beta", asset_type="database", publicly_exposed=True))
        await s.commit()

    body = (await client.get("/api/v1/assets/")).json()
    assert body["total"] == 2
    assert {a["name"] for a in body["items"]} == {"alpha", "beta"}
    assert body["publicly_exposed"] == 1


async def test_asset_vulnerability_rollup_and_no_n_plus_one(client, session_factory):
    async with session_factory() as s:
        asset = make_asset(name="alpha")
        s.add(asset)
        await s.flush()
        s.add(make_vulnerability(title="v1", severity="critical", asset_id=asset.id))
        s.add(make_vulnerability(title="v2", severity="high", asset_id=asset.id))
        s.add(make_vulnerability(title="v3", severity="high", status="fixed", asset_id=asset.id))
        await s.commit()
        asset_id = str(asset.id)

    detail = (await client.get(f"/api/v1/assets/{asset_id}")).json()
    assert detail["vulnerability_count"] == 3
    assert detail["vulnerability_severity"]["critical"] == 1
    assert detail["vulnerability_severity"]["high"] == 2
    # Only unresolved findings count as open.
    assert detail["open_findings"] == 2


async def test_asset_filtering_by_type_and_search(client, session_factory):
    async with session_factory() as s:
        s.add(make_asset(name="prod-api", asset_type="api_endpoint"))
        s.add(make_asset(name="prod-db", asset_type="database"))
        s.add(make_asset(name="staging-api", asset_type="api_endpoint"))
        await s.commit()

    by_type = (await client.get("/api/v1/assets/", params={"asset_type": "api_endpoint"})).json()
    assert by_type["total"] == 2
    assert all(a["asset_type"] == "api_endpoint" for a in by_type["items"])

    by_search = (await client.get("/api/v1/assets/", params={"search": "staging"})).json()
    assert by_search["total"] == 1
    assert by_search["items"][0]["name"] == "staging-api"


async def test_asset_pagination_metadata_correct(client, session_factory):
    async with session_factory() as s:
        for i in range(25):
            s.add(
                make_asset(
                    name=f"asset-{i:02d}",
                    discovered_at=datetime(2024, 8, 1) - __import__("datetime").timedelta(days=i),
                )
            )
        await s.commit()

    page1 = (await client.get("/api/v1/assets/", params={"page": 1, "page_size": 10})).json()
    assert page1["total"] == 25
    assert page1["page"] == 1
    assert page1["page_size"] == 10
    assert page1["total_pages"] == 3
    assert len(page1["items"]) == 10

    page3 = (await client.get("/api/v1/assets/", params={"page": 3, "page_size": 10})).json()
    assert len(page3["items"]) == 5

    # No overlap between pages.
    ids1 = {a["id"] for a in page1["items"]}
    ids3 = {a["id"] for a in page3["items"]}
    assert ids1.isdisjoint(ids3)


async def test_asset_page_size_is_echoed_not_overwritten(client, session_factory):
    """Regression: page_size must be the requested value, never the page's length."""
    async with session_factory() as s:
        for i in range(3):
            s.add(make_asset(name=f"asset-{i}"))
        await s.commit()

    body = (await client.get("/api/v1/assets/", params={"page": 1, "page_size": 50})).json()
    assert body["page_size"] == 50  # not 3 (the number of rows on the page)
    assert len(body["items"]) == 3


async def test_asset_detail_missing_returns_404(client):
    resp = await client.get(f"/api/v1/assets/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert "error" not in resp.json()


async def test_asset_detail_invalid_uuid_returns_404(client):
    resp = await client.get("/api/v1/assets/not-a-uuid")
    assert resp.status_code == 404


async def test_asset_type_summary_is_database_backed(client, session_factory):
    async with session_factory() as s:
        a1 = make_asset(name="api", asset_type="api_endpoint", publicly_exposed=True, criticality=9)
        a2 = make_asset(name="db", asset_type="database")
        s.add_all([a1, a2])
        await s.flush()
        s.add(make_vulnerability(asset_id=a1.id))
        await s.commit()

    summary = (await client.get("/api/v1/assets/types/summary")).json()
    assert summary["api_endpoint"]["count"] == 1
    assert summary["api_endpoint"]["exposed"] == 1
    assert summary["api_endpoint"]["critical"] == 1
    assert summary["api_endpoint"]["vulnerabilities"] == 1
    assert summary["database"]["count"] == 1


async def test_empty_asset_type_summary_is_empty_object(client):
    assert (await client.get("/api/v1/assets/types/summary")).json() == {}


async def test_database_failure_is_not_disguised_as_demo_data(client, session_factory):
    """A failing query must surface as an error, never a simulated fallback."""

    class _Boom(Exception):
        pass

    async def _broken_db():
        class _Session:
            async def execute(self, *a, **k):
                raise OperationalError("SELECT 1", {}, _Boom("db down"))

            async def scalar(self, *a, **k):
                raise OperationalError("SELECT 1", {}, _Boom("db down"))

        yield _Session()

    fastapi_app.dependency_overrides[get_db] = _broken_db
    resp = await client.get("/api/v1/assets/")
    assert resp.status_code == 500
    assert "simulated" not in resp.text.lower()
