"""Thin application entry: FastAPI app + health probe + scan API + dashboard."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router
from core.db import init_db

_WEB = Path(__file__).parent / "web"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create the database schema on startup."""
    init_db()
    yield


app = FastAPI(title="Guardrail Auditor", version="0.0.0", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the dashboard shell (a client of the /api endpoints)."""
    return FileResponse(_WEB / "index.html")


app.mount("/static", StaticFiles(directory=str(_WEB / "static")), name="static")
