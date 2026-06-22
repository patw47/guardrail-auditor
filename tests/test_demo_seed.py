"""S8: the demo seed populates a scan and is idempotent (no duplicate pile-up)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.repository import load_result
from core.tables import ScanRow
from tools.demo_seed import DEMO_TAG, seed


def test_demo_seed_populates_a_scan(session: Session) -> None:
    scan_id = seed()
    result = load_result(session, scan_id)
    assert result is not None
    assert result.items, "the demo scan should have findings"
    assert result.score.value > 0


def test_demo_seed_is_idempotent(session: Session) -> None:
    seed()
    seed()  # re-run must replace, not pile up
    demos = list(session.scalars(select(ScanRow).where(ScanRow.source_ref == DEMO_TAG)))
    assert len(demos) == 1
