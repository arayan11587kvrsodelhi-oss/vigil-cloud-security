"""Shared test fixtures.

The tests exercise the HTTP layer against a real (in-memory) SQLAlchemy engine
rather than the PostgreSQL instance in ``.env``. This keeps the suite hermetic and
independent of any local database, while still running the exact same queries the
application issues in production.

The engine is swapped in by overriding the ``get_db`` dependency, which is how the
app obtains a session, so the production engine/session configuration is left
untouched.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool


# ---------------------------------------------------------------------------
# SQLite compatibility for the PostgreSQL-specific column types
# ---------------------------------------------------------------------------
# The production models use PostgreSQL UUID and JSONB columns (see
# app/models/models.py). The test database is in-memory SQLite, which has no such
# types. These compilers render equivalent SQLite types ONLY inside this test
# process; the production schema and the PostgreSQL configuration are untouched.
@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "CHAR(36)"


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):  # noqa: ANN001
    return "JSON"


from app.core.database import Base, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models.models import Asset, Container, Vulnerability  # noqa: E402

# Import models so they register against Base.metadata before create_all.
import app.models  # noqa: F401,E402


@pytest.fixture
def anyio_backend():
    """Run anyio tests on asyncio only (trio is not a dependency)."""
    return "asyncio"


@pytest.fixture
async def engine():
    """A fresh in-memory SQLite database per test."""
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def client(session_factory):
    """Async HTTP client wired to the app with the test database."""

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    # raise_app_exceptions=False mirrors production behaviour: an unhandled
    # exception (e.g. a database outage) becomes a 500 response rather than being
    # re-raised into the test. This is what lets the suite assert that a failed
    # query surfaces as an error and is never disguised as a demo/simulated 200.
    transport = ASGITransport(app=fastapi_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------


def make_asset(
    name: str = "asset",
    asset_type: str = "cloud_instance",
    publicly_exposed: bool = False,
    criticality: int = 5,
    discovered_at: datetime | None = None,
) -> Asset:
    return Asset(
        id=uuid.uuid4(),
        name=name,
        asset_type=asset_type,
        provider="aws",
        region="us-east-1",
        ip_address="10.0.0.1",
        domain=f"{name}.internal",
        publicly_exposed=publicly_exposed,
        criticality=criticality,
        tags=["test"],
        asset_metadata={},
        discovered_at=discovered_at or datetime(2024, 8, 1, 9, 0, 0),
        last_seen_at=datetime(2024, 8, 1, 9, 0, 0),
        is_active=True,
    )


def make_vulnerability(
    title: str = "finding",
    severity: str = "high",
    status: str = "active",
    cve_id: str | None = "CVE-2024-0001",
    cvss_score: float | None = 8.0,
    cisa_kev: bool = False,
    exploit_available: bool = False,
    asset_id=None,
    discovered_at: datetime | None = None,
) -> Vulnerability:
    return Vulnerability(
        id=uuid.uuid4(),
        cve_id=cve_id,
        title=title,
        description="test finding",
        cvss_score=cvss_score,
        cvss_vector="CVSS:3.1/AV:N",
        severity=severity,
        cisa_kev=cisa_kev,
        exploit_available=exploit_available,
        affected_component="log4j-core",
        fixed_version="2.17.1",
        status=status,
        discovered_at=discovered_at or datetime(2024, 8, 1, 9, 0, 0),
        updated_at=datetime(2024, 8, 1, 9, 0, 0),
        references=[],
        asset_id=asset_id,
    )


def make_container(name: str = "container", privileges: str = "standard") -> Container:
    return Container(
        id=uuid.uuid4(),
        name=name,
        image="registry.internal/img:1.0",
        status="running",
        privileges=privileges,
        exposed_ports=[],
        environment_vars={},
    )
