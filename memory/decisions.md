# decisions.md — design forks later sprints must honor

_(SCRIBE; re-read at sprint start. Write only what a later sprint needs.)_

## S0
- **Layered source tree** (`api/ core/ rules/ models/`) over a single `app/`.
  Each is a tracked package via `__init__.py`. Fills: models@S1, rules@S2,
  core scoring@S3, api + core pipeline@S5.
- **pyproject.toml is the single dependency source of truth** — no
  `requirements.txt`. Install/CI: `pip install -e ".[dev]"`.
- **core/ is the data layer; `core/db.py` is the thin SQLite layer**
  (`engine` / `SessionLocal` / `Base(DeclarativeBase)` / `init_db()`). NO domain
  tables yet — the concrete schema (Scan/Finding/Score/Control) is the **S5
  sensitive gate**; tables register on `Base` there.
- **Governance files at repo root**, byte-for-byte as approved (CLAUDE.md must be
  root to auto-load).
- **DB path** `./guardrail.db` (gitignored). `init_db()` is a no-op create until
  tables register at S5.
- **Thin app entry** `main.py` creates the FastAPI app + `/health`; domain
  routers accrete under `api/` and are included here at S5.
