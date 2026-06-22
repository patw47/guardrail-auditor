# lessons.md — bugs, root causes, caught regressions

_(SCRIBE; re-read at sprint start. Write only what a later sprint needs.)_

## S0
- No bug this sprint. One note for **S5** integration tests: a bare
  `TestClient(app)` does NOT trigger FastAPI lifespan, so `init_db()` is not
  exercised by `test_health`. When DB-backed endpoints arrive, drive them with
  `with TestClient(app) as client:` so startup (DB init) runs.
