"""Thin application entry: FastAPI app + health probe + scan API router."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from core.db import init_db


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
