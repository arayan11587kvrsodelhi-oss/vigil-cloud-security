

## Local development

All commands below are PowerShell and are run from the repository root unless a
`cd` is shown.

### Backend - one-time setup

Create the virtual environment (skip if `backend/.venv` already exists) and
install the runtime dependencies:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

### Run the backend
```powershell
python run_backend.py
```
The API listens on `http://127.0.0.1:8000` (docs at `/api/docs`, health at
`/api/health`). Requires the PostgreSQL instance referenced by `DATABASE_URL` in
`backend/.env`; `init_db()` creates the eight tables on startup.

### Backend - install development/test dependencies

Installs the runtime requirements plus the test runner (`pytest`) and the async
SQLite driver (`aiosqlite`) used by the in-memory test database:
```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
cd ..
```
Do not relax the `anyio` pin: FastAPI 0.104.1 requires `anyio>=3.7.1,<4.0.0`.

### Run backend tests
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```
The suite is hermetic - it swaps in an in-memory SQLite database via a
dependency override, so it does **not** touch the configured PostgreSQL database.

### Frontend - install dependencies
```powershell
cd frontend
npm install
```

### Run the frontend (dev server)
```powershell
cd frontend
npm run dev
```

### Build the frontend (production)
```powershell
cd frontend
npm run build
```
This runs `tsc` (type check) followed by `vite build`, emitting `frontend/dist/`.

## Data model (PostgreSQL)

VIGIL is genuinely database-backed for its core inventory. The `assets` and
`vulnerabilities` endpoints, along with the dashboard summary and security score,
read from PostgreSQL via the async SQLAlchemy engine configured in
`backend/app/core/config.py` (`DATABASE_URL`). The eight tables (`assets`,
`vulnerabilities`, `attack_paths`, `containers`, `iam_roles`, `network_routes`,
`secrets`, `scan_results`) are created by `init_db()` on startup.

Empty tables return empty collections and zero totals — VIGIL does not fabricate
records. If a database query fails, the API returns an error; it never silently
falls back to demo data.

## Demo mode (development only)

Some capabilities have no live integration (no attack-graph solver, secret
scanner, container scanner, SBOM generator, or SCM integration is connected).
Those endpoints return clearly-labelled **simulated** fixtures and set
`"simulated": true` plus `"source_state": "simulated"` in every response.

Demo fixtures are only served for the core asset/vulnerability endpoints when you
explicitly opt in by setting `ENABLE_DEMO_MODE=true` in `backend/.env`. It defaults
to `false`, so simulated records are never presented as real security findings.
Even when demo mode is on, a failing database query still surfaces as an error.

## Verifying persistence

The API exposes read endpoints for assets and vulnerabilities. To confirm a record
survives a restart:

1. Start the backend (`python run_backend.py`).
2. Insert a row with `psql` (or any SQL client):
   ```sql
   INSERT INTO assets (id, name, asset_type, publicly_exposed, criticality,
                       discovered_at, last_seen_at, is_active)
   VALUES (gen_random_uuid(), 'persistence-check', 'cloud_instance', false, 1,
           now(), now(), true);
   ```
3. `GET http://127.0.0.1:8000/api/v1/assets/?search=persistence-check` and note the
   returned `id`.
4. Stop the backend (Ctrl+C) and start it again.
5. Repeat the request — the record is still returned, confirming it was persisted
   to PostgreSQL rather than held in process memory.
6. Remove the row when finished.
