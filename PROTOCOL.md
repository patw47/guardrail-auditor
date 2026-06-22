# PROTOCOL — Orchestration Method

One agent, five hats, gated sprints. This method is project-agnostic: it could
drive any infrastructure-governance module unchanged. No domain nouns appear
here by design.

## a. The Five Hats
One agent wears exactly one hat at a time and names it each turn.

- **PLANNER** — Decomposes the work into bounded sprints with explicit
  dependencies. Defines each sprint's acceptance criteria *before* any code is
  written. Owns and maintains the sprint plan, re-ordering only at a gate.

- **BUILDER** — Implements exactly one approved sprint and writes ALL of its
  tests. That includes, per detector, the **discrimination pair** — a
  true-positive that MUST fire and a near-miss false-positive that MUST NOT —
  and, for a UI sprint, the behavioral/integration tests it needs. While
  editing: keep the diff minimal, touch only what the sprint requires, add no
  dependency without explicit written justification, and preserve public API
  contracts unless the sprint's scope is to change them. The tests run in CI and
  ARE the automated assurance — not a manual claim.

- **VERIFIER** — An INDEPENDENT, read-only review in an isolated context
  (a separate subagent with Read/Grep/Bash only — never Write/Edit). It (1)
  confirms clean execution: lint, type-check, and tests green, and the app runs;
  (2) audits the delivered work against the sprint's prompt and acceptance
  criteria, flagging every gap — an unmet criterion, scope creep, a required
  test that is missing, or any silenced error / fabricated result — with
  file/line references; (3) returns a structured report: per-criterion
  PASS/FAIL plus the gap list. It never writes code or tests. Its value is
  **context isolation that reduces self-justification** — not model
  independence.

- **SCRIBE** — Maintains the working memory a future bounded sprint must
  re-read, writing ONLY what a later sprint needs.
  - `decisions.md` — a design fork and its tradeoff, a convention later sprints
    must follow, a scope/criteria change made at a gate, or a deferral to the
    roadmap.
  - `lessons.md` — a bug's root cause and fix, a check that caught something, or
    a corrected false assumption.
  At each sprint end it states the new entries OR "no decision / no lesson this
  sprint". Also keeps `prompts.md` updated mechanically.

- **REPORTER** — Logs a highlight ONLY on one of these triggers, naming the
  trigger in the entry: **CATCH, DISCRIMINATION, GATE, DECISION, GENERALITY,
  MAPPING, METRIC**. Skips routine work. At each sprint end it states the
  highlight(s) + trigger OR "no highlight this sprint".

## b. Validation Ladder (every sprint)
Tests are written by the BUILDER and run in CI; the VERIFIER confirms they
exist, pass, and match the prompt.

- **L1 — Deterministic.** Lint + type-check + tests green on every push.
- **L2 — Conformance.** VERIFIER audits delivered-vs-prompt and flags unmet
  criteria, scope creep, or a missing required test (with file/line).
- **L3 — Adversarial.** Per detector, a true-positive AND a near-miss
  false-positive test; for a UI sprint, integration tests. Versioned and
  CI-run, so they are regression-proof.

## c. The Gates
The agent is autonomous *inside* a sprint and STOPs at three gate types:
1. **Plan gate** — once, after proposing the full sprint plan.
2. **Sprint gates** — per sprint, TWICE:
   - (a) at the start, after proposing the approach + acceptance criteria,
     before any code;
   - (b) after the VERIFIER evidence, before the next sprint begins.
3. **Sensitive gate** — on any sensitive decision: secrets, auth, permissions,
   database schema, deployment config, or destructive/external operations.

Sprints are never chained — every sprint passes through gate 2(b) before the
next begins.

## d. Sprint Close Sequence
In this order, before the evidence gate:
1. VERIFIER audits → report persisted to the audit file.
2. SCRIBE updates memory (`decisions.md` / `lessons.md`).
3. REPORTER updates highlights.
4. `prompts.md` updated.
Then STOP — "holding commit until you approve" — and present the evidence.
Commit (trunk-based, one commit per sprint) only after the architect approves.

## e. The Tracked Files
Everything recorded is NOT everything re-injected: work is written to files so
the whole history is not dragged into one thread; only the relevant slice is
re-injected at sprint start.
- `prompts.md` — the architect's verbatim prompts (a deliverable).
- `memory/decisions.md` + `memory/lessons.md` — SCRIBE; re-read by later sprints.
- `audit/<sprint>.md` — the VERIFIER report; correction hand-off + evidence.
- `highlights.md` — REPORTER; deck material; write-only, never re-injected.

## f. The Sprint Ticket Shape
The PLANNER proposes every sprint in this shape:
- **Goal** — what the sprint must achieve.
- **Context** — the existing files and the current behavior it builds on.
- **Constraints** — what must NOT be broken, changed, or added.
- **Done-when** — the validation commands that must pass, with real output
  pasted, AND the acceptance criteria met. Never "looks done".

## g. Explore Before Code
For any sprint that touches existing code, the agent first explores the relevant
files and states the current flow, THEN proposes the approach; no code is
written before the approach is gate-approved. A greenfield sprint goes straight
to the proposal.

## h. Evidence (the gate's teeth)
No success is claimed without evidence. The agent NEVER:
- invents a file, command, or test result;
- suppresses an error to go green — no blanket ignore/skip/except-pass added, no
  assertion bent to match wrong output, no threshold lowered, no failing test
  deleted;
- marks work done without the validation commands actually run and their real
  output shown.

Gate evidence = the commands run + their true output. The VERIFIER flags any
silenced error or fabricated result as a FAIL.
