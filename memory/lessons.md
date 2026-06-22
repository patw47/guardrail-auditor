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

## S2
- **hcl2 v8 wraps heredocs in `<<TAG` … `TAG`** around the body, so a heredoc
  policy is NOT directly `json.loads`-able. The L3 TP test caught it (the
  public-via-policy detector stayed silent). Fixed detector-local with
  `_strip_heredoc` in `rules/detectors.py`. Candidate S1 follow-up (roadmap):
  normalize heredoc bodies in the parser so no consumer sees `<<TAG`.
- **Don't reference a doc from code before the doc exists.** `detectors.py`
  said severities were "documented in decisions.md" while the S2 section wasn't
  written yet — the VERIFIER (rightly) FAILed H2 on the dangling reference. Land
  the doc in the same change as the code that cites it.

## S3
- No bug this sprint. Applied the S2 lesson: wrote the `decisions.md` S3 dials
  (weights/bands/floor) in the SAME change as `core/scoring.py`, so the
  VERIFIER's D3 doc-vs-code check passed first time — no H2-style doc-drift FAIL.

## S4
- **Compliance control numbering drifts across benchmark versions — verify, never
  recall.** CIS AWS S3 Block-Public-Access was `2.1.5` in v1.4 but `2.1.4` in the
  pinned v3.0.0; SSH was `4.x` in v1.2 but `5.2` in v3.0.0. Source-checked each
  against v3.0.0 (same method as the S2 severities). When a precise sub-number
  isn't verifiable (CIS RDS), cite the section with a visible `(section)` marker
  rather than guess — a fabricated control id is the worst credibility hit for an
  audit tool.
