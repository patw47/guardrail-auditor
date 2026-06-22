"""Thin SQLite layer: engine, session, declarative base, init.

Deliberately thin for S0 — NO domain tables. The concrete schema
(Scan/Finding/Score/Control) is the S5 sensitive gate and accretes there.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./guardrail.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base. Domain tables register on this in later sprints (S5)."""


def init_db() -> None:
    """Create all tables registered on ``Base``.

    Thin at S0: no domain tables are registered yet, so this is a no-op create
    that simply opens the SQLite file. Tables accrete from S5.
    """
    Base.metadata.create_all(bind=engine)
