"""Thin SQLite layer: engine, session, declarative base, init.

The schema itself lives in core/tables.py (registered on Base); db.py only owns
the connection, session factory, base, and init. The DB URL is env-overridable
(DATABASE_URL) so tests can point at an isolated temp database.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./guardrail.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base. Domain tables (core/tables.py) register on this."""


def init_db() -> None:
    """Create all tables registered on ``Base``."""
    from core import tables  # noqa: F401  -- import registers the ORM models on Base

    Base.metadata.create_all(bind=engine)
