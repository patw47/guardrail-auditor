"""Regression: a dev guardrail.db created BEFORE the S5b `source_ref` column must
be upgraded in place on boot — not 500'd on a repo scan."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from core.db import Base, _reconcile_dev_schema
from core.tables import ScanRow  # importing registers all ORM tables on Base


def _old_schema_engine(path: Path) -> Engine:
    """A pre-S5b database: a `scans` table with NO `source_ref` column."""
    eng = create_engine(f"sqlite:///{path}")
    with eng.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE scans ("
                "id VARCHAR PRIMARY KEY, created_at DATETIME, "
                "source_type VARCHAR, file_count INTEGER)"
            )
        )
    return eng


def _columns(eng: Engine, table: str) -> set[str]:
    return {col["name"] for col in inspect(eng).get_columns(table)}


def test_stale_db_is_upgraded_with_the_missing_column(tmp_path: Path) -> None:
    eng = _old_schema_engine(tmp_path / "old.db")
    assert "source_ref" not in _columns(eng, "scans")

    # the init_db path: create_all (adds the other tables) + reconcile (adds the column)
    Base.metadata.create_all(bind=eng)
    _reconcile_dev_schema(eng)

    assert "source_ref" in _columns(eng, "scans")


def test_upgraded_db_persists_and_reads_a_repo_scan(tmp_path: Path) -> None:
    eng = _old_schema_engine(tmp_path / "old.db")
    Base.metadata.create_all(bind=eng)
    _reconcile_dev_schema(eng)

    session = sessionmaker(bind=eng)()
    try:
        # a repo scan sets source_ref — exactly what 500'd before the fix
        session.add(
            ScanRow(
                id="s1",
                created_at=datetime.now(UTC),
                source_type="repo_url",
                file_count=1,
                source_ref="https://github.com/owner/repo",
            )
        )
        session.commit()
        row = session.get(ScanRow, "s1")
        assert row is not None
        assert row.source_ref == "https://github.com/owner/repo"  # read back, no 500
    finally:
        session.close()


def test_reconcile_is_a_noop_on_a_current_schema_db(tmp_path: Path) -> None:
    eng = create_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    Base.metadata.create_all(bind=eng)
    before = _columns(eng, "scans")
    _reconcile_dev_schema(eng)  # nothing missing → no ALTER
    after = _columns(eng, "scans")
    assert before == after
    assert "source_ref" in after
