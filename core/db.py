"""Thin SQLite layer: engine, session, declarative base, init.

The schema itself lives in core/tables.py (registered on Base); db.py only owns
the connection, session factory, base, and init. The DB URL is env-overridable
(DATABASE_URL) so tests can point at an isolated temp database.
"""

from __future__ import annotations

import os

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./guardrail.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base. Domain tables (core/tables.py) register on this."""


def init_db() -> None:
    """Create the schema, then add any column a stale dev SQLite db is missing.

    `create_all` emits CREATE TABLE IF NOT EXISTS, so it will NOT add a new column
    to a table that already exists — a `guardrail.db` created before a column was
    added keeps the old shape and 500s on insert/read. `_reconcile_dev_schema`
    adds the missing nullable column(s): additive only, no data loss, no Alembic.
    """
    from core import tables  # noqa: F401  -- import registers the ORM models on Base

    Base.metadata.create_all(bind=engine)
    _reconcile_dev_schema(engine)


def _reconcile_dev_schema(bound_engine: Engine) -> None:
    """Add any model column missing from an existing table (additive, nullable only).

    A no-op for a current-schema database — only an out-of-date dev SQLite file
    triggers an ALTER. Never drops or alters existing columns/data.
    """
    inspector = inspect(bound_engine)
    existing = set(inspector.get_table_names())
    with bound_engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing:
                continue  # create_all already made it
            present = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in present:
                    continue
                addable = (
                    column.nullable
                    or column.default is not None
                    or column.server_default is not None
                )
                if not addable:
                    continue  # can't safely backfill a NOT NULL column on existing rows
                col_type = column.type.compile(dialect=bound_engine.dialect)
                conn.execute(
                    text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type}')
                )
