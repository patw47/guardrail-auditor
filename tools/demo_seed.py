#!/usr/bin/env python
"""Seed the dev database with a demo scan so the dashboard shows data on first run.

Offline (scans the bundled vulnerable fixtures — no clone). Idempotent: the demo
scan is tagged, and re-running replaces it rather than piling up duplicates.

    ./.venv/bin/python tools/demo_seed.py
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from core.config_source import UploadedFilesSource
from core.db import SessionLocal, init_db
from core.pipeline import run_scan
from core.repository import save_scan
from core.tables import ScanRow

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "detectors" / "multi_violation.tf"
DEMO_TAG = "__demo__"  # source_ref marker so the seed is idempotent


def seed() -> str:
    init_db()
    session = SessionLocal()
    try:
        # idempotent: drop any previous demo scan (cascades to its rows)
        for row in session.scalars(select(ScanRow).where(ScanRow.source_ref == DEMO_TAG)):
            session.delete(row)
        session.commit()

        result = run_scan(UploadedFilesSource([("multi_violation.tf", FIXTURE.read_text())]))
        return save_scan(session, result, source_ref=DEMO_TAG)
    finally:
        session.close()


def main() -> int:
    scan_id = seed()
    print(f"seeded demo scan {scan_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
