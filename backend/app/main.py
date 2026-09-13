from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import close_redis
import app.models  # Ensure all SQLAlchemy models are registered
from app.api.dashboard import router as dashboard_router
from app.api.vulnerabilities import router as vulnerabilities_router
from app.api.assets import router as assets_router
from app.api.attack_paths import router as attack_paths_router
from app.api.devsecops import router as devsecops_router
from app.api.ai_analyst import router as ai_analyst_router
from app.api.scans import router as scans_router
from app.api.secrets import router as secrets_router
from app.api.ws import router as ws_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        print(f"[VIGIL] Database initialization warning (PostgreSQL offline or unconfigured): {e}")
    yield
    try:
        await close_redis()
    except Exception as e:
        print(f"[VIGIL] Redis shutdown warning: {e}")
    try:
        await close_db()
    except Exception as e:
        print(f"[VIGIL] Database shutdown warning: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(vulnerabilities_router, prefix="/api/v1/vulnerabilities", tags=["Vulnerabilities"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(attack_paths_router, prefix="/api/v1/attack-paths", tags=["Attack Paths"])
app.include_router(devsecops_router, prefix="/api/v1/devsecops", tags=["DevSecOps"])
app.include_router(ai_analyst_router, prefix="/api/v1/ai", tags=["AI Analyst"])
app.include_router(scans_router, prefix="/api/v1/scans", tags=["Scans"])
app.include_router(secrets_router, prefix="/api/v1/secrets", tags=["Secrets"])
app.include_router(ws_router, prefix="/ws", tags=["WebSockets"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "service": settings.APP_NAME}