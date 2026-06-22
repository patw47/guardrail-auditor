# lessons.md — bugs, root causes, caught regressions

_(SCRIBE; re-read at sprint start. Write only what a later sprint needs.)_

## S0
- No bug this sprint. One note for **S5** integration tests: a bare
  `TestClient(app)` does NOT trigger FastAPI lifespan, so `init_db()` is not
  exercised by `test_health`. When DB-backed endpoints arrive, drive them with
  `with TestClient(app) as client:` so startup (DB init) runs.

## S1
- **Probe the library before coding the mapper.** A build-time probe of
  `python-hcl2` showed v8.1.2 differs from older docs: `with_meta` is gone,
  scalars are quote-wrapped, blocks are always lists with an `__is_block__`
  marker. Coding to the assumed (older) shape would have shipped wrong
  line-handling and quoted values. Rule for future parser/lib work: probe the
  real output shape first, don't trust remembered API docs.
