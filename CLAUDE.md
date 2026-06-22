# CLAUDE.md — Standing Rules (auto-loaded every turn)

Method is in **PROTOCOL.md** (read it; do not duplicate). Domain binding is in
**ADAPTER.md**. Always-on rules only:

- **Single tool = you, end-to-end.** Switching model is fine; switching tool is not.
- **The loop:** PLANNER proposes one bounded sprint → gate → BUILDER builds + all
  tests → VERIFIER audits → SCRIBE/REPORTER log → gate → commit. One sprint at a
  time; never chain.
- **Explore before editing.** State the current flow first; no code before the
  approach is gate-approved.
- **Minimal diff.** Touch only what the sprint needs; no new dependency without
  written justification; preserve public API contracts.
- **Evidence or it didn't happen.** No success claimed without the commands run +
  their real output. Never silence an error to go green (no blanket
  ignore/skip/except-pass, no bent assertion, no lowered threshold, no deleted
  failing test).
- **Git:** trunk-based; one commit per sprint, pushed only after the architect's gate.
- **Each sprint end:** update `prompts.md`, `memory/` (decisions + lessons),
  `highlights.md`.
- **Commands:**
  - lint: `ruff check .`
  - type-check: `mypy .`
  - tests: `pytest -q`
