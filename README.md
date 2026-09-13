

## Local development

Backend (from the project root):
```powershell
python run_backend.py
```
Frontend (separate terminal):
```powershell
cd frontend
npm install
npm run dev
```
Health check: `http://127.0.0.1:8000/api/health`

PostgreSQL is optional for the demo/API-ready fallback; a database initialization warning is expected when PostgreSQL is not running.
