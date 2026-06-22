"""Test config — isolate the database to a temp file BEFORE the app imports it."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest  # noqa: E402  -- DATABASE_URL must be set before core.db imports
from sqlalchemy.orm import Session  # noqa: E402

from core.db import SessionLocal, init_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Iterator[None]:
    init_db()
    yield


@pytest.fixture
def session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
