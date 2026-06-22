# Verification — stale dev SQLite db missing `source_ref` (additive in-place upgrade)

**Scope:** single-fix patch. `init_db()`'s `create_all` (CREATE TABLE IF NOT EXISTS) never
adds a column to an existing `scans` table, so a `guardrail.db` made before the S5b
`source_ref` column 500s on repo scans. Fix: `core/db.py::_reconcile_dev_schema` ALTERs in
the missing nullable/defaulted column(s) on boot.

## L1 (run from repo root, `./.venv/bin/...`)

| Gate   | Result | Exit |
|--------|--------|------|
| ruff check . | `All checks passed!` | 0 |
| mypy .       | `Success: no issues found in 47 source files` | 0 |
| pytest -q    | `88 passed, 1 warning in 1.47s` | 0 |
| pytest tests/test_schema_migration.py -v | 3 passed (upgrade / round-trip / no-op) | 0 |

The lone warning is a pre-existing StarletteDeprecationWarning (httpx), unrelated to the patch.

## Criteria

| # | Criterion | Verdict | Evidence |
|---|-----------|---------|----------|
| 1 | L1 ruff/mypy/pytest all green | PASS | ruff exit 0; mypy exit 0 (47 files); pytest 88 passed exit 0 |
| 2 | OLD-schema `scans` (no `source_ref`) upgraded in place by init_db; repo scan persists + reads back, no 500 | PASS | `tests/test_schema_migration.py:34-42` (column added), `:45-67` (round-trip). LIVE REPRO: old cols `[created_at,file_count,id,source_type]` -> after `init_db()` `[...,source_ref,...]`; insert ScanRow(source_ref="https://github.com/owner/repo") + select -> value round-trips, no OperationalError. NEGATIVE CONTROL (create_all without `_reconcile`) raises exactly `(sqlite3.OperationalError) table scans has no column named source_ref` — bug is real and the fix removes it. |
| 3 | Fix is ADDITIVE + SAFE: only `ALTER TABLE ADD COLUMN` for missing nullable/defaulted cols; never drops/recreates; no-op on current-schema db | PASS | `core/db.py:39-65` — iterates `Base.metadata.sorted_tables`, skips tables not in `inspector.get_table_names()`, skips columns already `present`, guards `addable = nullable or default is not None or server_default is not None`, only emits `ALTER TABLE ... ADD COLUMN`. No DROP/CREATE/recreate anywhere. No-op test `tests/test_schema_migration.py:70-77` asserts `before == after`. GUARD TEST: a NOT NULL no-default column missing from an existing table is skipped (not ALTERed), no crash. |
| 4 | Persistence identical for a correct db; normal upload + repo scans still pass | PASS | No-op test (`:70-77`) — fresh db columns unchanged. Existing API tests pass unchanged: `tests/test_api.py`, `tests/test_repo_api.py`, `tests/test_repo_source.py`, `tests/test_dashboard.py`, `tests/test_demo_seed.py` all within the 88 passed. |

## Constraints

| ID | Constraint | Verdict | Evidence |
|----|-----------|---------|----------|
| C1 | Detection/scoring/compliance/parsing UNCHANGED; only core/db.py + new test + README touched | PASS (code) | `git diff --stat HEAD -- rules/ core/scoring.py core/compliance.py core/parsing/ core/remediation.py models/` is EMPTY. Tracked code changes: `core/db.py` (+38/-2), `README.md` (+4). New: `tests/test_schema_migration.py`. SEE NOTE below re `prompts.md`. |
| C2 | NO new dependency; uses only sqlalchemy (inspect/text/Engine), already a dep | PASS | `git diff HEAD -- pyproject.toml` EMPTY. `core/db.py:9` imports `Engine, create_engine, inspect, text` from sqlalchemy (existing dep, `pyproject.toml:13` `sqlalchemy>=2.0`). |
| C3 | NO Alembic / migration framework | PASS | All `alembic` grep hits are in `.venv/` (3rd-party SQLAlchemy/pip), the verbatim prompt log, and the db.py docstring stating "no Alembic". No alembic import, config, or dep. |
| C4 | NO schema redesign; core/tables.py unchanged; column pre-existed from S5b | PASS | `git diff --stat HEAD -- core/tables.py` EMPTY. `core/tables.py:25` `source_ref: Mapped[str \| None] = mapped_column(nullable=True, default=None)` — already nullable+defaulted. |

## Tampering hunt

- No `skip`/`xfail`/`pytest.mark`/`assert True`/empty-body cheats in the new test — grep returned nothing.
- Asserts are real conditions: column membership change (`source_ref in columns`), value round-trip
  (`row.source_ref == "https://github.com/owner/repo"`), and structural equality (`before == after`).
- ALTER is guarded by `addable` (nullable OR default OR server_default) — verified live that a NOT NULL,
  no-default column is skipped, so it cannot crash backfilling existing rows.
- Negative control proves the test would fail without the fix (pre-fix path 500s with the exact error).

## Note (non-blocking deviation)

`prompts.md` (+18/-1) is also modified. It is this repo's verbatim SCRIBE prompt log
("Architect prompts logged verbatim, every turn") — it records the bug prompt itself and contains
zero code/logic. It is outside C1's detection/scoring/compliance/parsing scope and affects no criterion,
but it is a third tracked file beyond the strict "core/db.py + test + README" wording. Flagged, not failing.

## VERDICT: PASS

The old-schema db no longer 500s (live repro + negative control confirm). The fix is additive
(ALTER ADD COLUMN only, nullable/defaulted-guarded), never drops/recreates, and is a verified no-op
on a current-schema db. Detection/scoring/compliance/parsing/models diff is EMPTY; core/tables.py and
pyproject.toml unchanged; no new dependency; no Alembic. L1 fully green (ruff/mypy/pytest exit 0).
