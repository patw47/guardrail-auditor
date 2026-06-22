"""Thin application entry: FastAPI app + health probe.

Domain routers accrete under `api/` at S5; this entry stays thin.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise the (thin) database on startup. No domain tables yet (S5)."""
    init_db()
    yield


app = FastAPI(title="Guardrail Auditor", version="0.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
