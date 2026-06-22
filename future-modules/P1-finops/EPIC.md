# EPIC — P1 FinOps: Cloud Cost Optimizer

> **Honesty line.** This is a **ready-to-execute SPECIFICATION, not a built
> module** — no code, no scaffold here. It is driven by the **same approved
> `PROTOCOL.md`** as P2 (the orchestration method is project-agnostic by design);
> only `ADAPTER.md`'s two clauses change. **No invented metrics** — the `$-saved`
> figures are values the tool would *compute* from the billing export, not
> benchmarks claimed here.

## 1. The Seam — same PROTOCOL.md, only the adapter changes

The method is **referenced, not rewritten**. Reuse P2's `PROTOCOL.md` unchanged:
the five hats (PLANNER/BUILDER/VERIFIER/SCRIBE/REPORTER), the L1/L2/L3 validation
ladder, the two-gate-per-sprint loop, the sprint ticket shape, the tracked files
(`prompts.md` / `memory/` / `audit/<sprint>.md` / `highlights.md`), and the
evidence rules. Reuse `CLAUDE.md` and `.claude/agents/verifier.md` as-is.

What swaps (the **only** module-specific surface):

| | clause 1 — domain layer | clause 2 — L3 false-positive trap |
|---|---|---|
| P2 (built) | finding → named control → **Risk Score** | public-via-policy bucket flags; private+versioning doesn't |
| **P1 (this)** | waste finding → FinOps category → **$-saved estimate** | orphaned (unattached ≥30d) disk flags; attached-but-low-IO disk **doesn't** |

**Identical across all three modules:** detector → discrimination pair · the
deterministic aggregate score · map-to-named-taxonomy + explanation · assurance
(coverage matrix + external oracle). That is what makes three projects *one
method*.

## 2. ADAPTER — the 2 clauses (this is the whole module-specific delta)

**Clause 1 — domain layer (universal shape):**
`waste finding → FinOps category → $-saved estimate`
- Every finding maps to a **named FinOps category** (e.g. *orphaned resource*,
  *idle resource*, *over-provisioned*) with a reference, and carries a
  **deterministic $-saved estimate** derived from the resource's billed cost.
- Findings aggregate into a **total potential monthly savings** (the analogue of
  the Risk Score). Explanation is a deterministic template; any LLM narration is
  fenced out of the estimate/category trust path.

**Clause 2 — L3 false-positive trap (the domain discriminator):**
- **TRUE-POSITIVE — MUST flag:** a genuinely orphaned disk (unattached for ≥30d).
- **NEAR-MISS — MUST NOT flag (never suggest deleting):** a disk that *looks*
  idle but is **attached / low-IO**. *Idle ≠ orphaned.*

## 3. Vision (brief)

- **What/why:** ingest AWS/Azure billing exports, find waste (orphaned/idle
  resources), estimate $-saved, and generate the decommission action — FinOps
  shift-left, before the spend recurs.
- **In scope:** static analysis of billing exports (JSON/CSV); deterministic
  detectors + $-saved; FinOps-category mapping; decommission CLI/API generation;
  REST API; dashboard.
- **Out of scope:** no live cloud calls, no actual deletion (generate the
  command, never run it), no API key required for the core.
- **MVP success:** runs with no cloud creds; flags orphaned-disk/idle-VM and does
  **not** flag the attached/low-IO look-alike; estimates $-saved; produces the
  decommission command; dashboard shows total savings; deterministic.

## 4. Sprint decomposition

Cross-cutting (per PROTOCOL): **L1** lint+type+tests every sprint · **L2**
VERIFIER conformance · **L3** discrimination pair per detector. Two gates per
sprint. MVP boundary = the dashboard (S7); assurance (S8) is the post-MVP
differentiator.

- **S0 — Scaffold + governance-on-disk.** Goal: project tree, the reused
  governance files written verbatim (PROTOCOL/CLAUDE/verifier) + the swapped
  ADAPTER, FastAPI/SQLite skeleton, CI. *Deps: —.* Accept: L1 green; `/health`
  200; governance files on disk; CI runs the ladder.
- **S1 — Ingest billing exports.** Goal: parse AWS CUR + Azure billing export
  (JSON/CSV) into a normalized `ResourceUsage` (id, type, region, monthly cost,
  attachment + usage signals). *Deps: S0.* Accept: real export fixtures parse
  with correct cost + signals; malformed rejected cleanly; both formats tested.
- **S2 — Waste detectors [first L3 sprint].** *(full ticket shape below.)*
- **S3 — $-saved scoring.** Goal: a pure function `findings → per-finding $-saved
  + total potential monthly savings`. *Deps: S2.* Accept: same input → same total
  (determinism test); no findings → $0; per-finding breakdown returned; figures
  derived only from billed cost (no invented numbers).
- **S4 — FinOps category mapping + explanation.** Goal: `finding → named FinOps
  category (+ reference)` via a deterministic table + a pure `render()`. *Deps:
  S3.* Accept: every finding maps to ≥1 named category; render pure; no category
  outside the table (fence test).
- **S5 — Remediation (decommission action).** Goal: per finding, generate the
  **decommission CLI/API command** (e.g. `aws ec2 delete-volume --volume-id …`).
  *Deps: S4.* Accept: each detector type has a remediation; pure + fenced;
  **never executes** the command (generates text only) — asserted.
- **S6 — REST API + persistence + uploaded-export ConfigSource.** Goal: wire the
  pipeline behind REST, persist a scan (schema = sensitive gate). *Deps: S5.*
  Accept: POST export → 201 with findings + $-saved; write→read round-trip
  identical; OpenAPI documents every endpoint.
- **S7 — Dashboard. ← MVP COMPLETE.** Goal: a FastAPI-served dashboard
  (API-only): total-$-saved gauge + waste table (category, $-saved, the
  decommission command) + empty/error states. *Deps: S6.* Accept: renders a
  scan from the API; no API key; behavioral/integration test.
- **S8 — Assurance (post-MVP differentiator).** Goal: coverage matrix from the
  CI discrimination tests + an external oracle (a reference cost/Trusted-Advisor-
  style labelled fixture set), **K→K agreement** on the implemented subset.
  *Deps: S2 + S6.* Accept: matrix lists every detector's TP+near-miss verdict
  (CI-sourced); oracle agreement recorded with pinned reference; divergences →
  LIMITATIONS.md (labelled WIN vs limitation); completeness stated honestly.

### S2 ticket — Waste detectors (build-ready, P2-S2 shape)
- **Goal:** a deterministic detector engine over `ResourceUsage` → waste
  findings, with the detectors: **orphaned unattached disk** + **idle VM**
  (must-have); **unattached EIP** + **stale snapshot** (amplification). Each maps
  AWS + Azure native shapes onto one rule.
- **Context:** consumes S1's normalized `ResourceUsage`; `rule_id` is the S4
  category join key; finding carries the signal that justified it (for $-saved).
- **Constraints:** detect-only (no scoring/mapping/persistence); no new
  dependency; engine deterministic (sorted output); **every shipped detector has
  BOTH tests** — never a detector without its FP-trap.
- **Eject rule:** if long, ship the 2 must-haves green WITH their discrimination
  pairs and record the other 2 as next-up.
- **Done-when (validation commands pass + criteria met):**
  1. `ruff` / `mypy` / `pytest` green.
  2. **Per detector, the discrimination pair exists as committed CI tests:** a
     true-positive fixture makes exactly that detector fire (correct
     rule/resource/$-signal) **AND** a near-miss fixture makes it stay silent.
  3. **Clause-2 trap, verbatim, as CI tests:** an orphaned unattached-≥30d disk
     **fires**; an attached-but-low-IO disk **stays silent** (idle ≠ orphaned).
  4. Engine deterministic: shuffled input → identical ordered findings.
  5. A multi-waste fixture → all expected findings, each carrying its category
     key + $-signal.

## 5. Roadmap / out of scope
- Cloud-billing source behind the same `ConfigSource` (read-only fetch from a
  billing export location, safety-guarded — the SSRF analogue). Post-MVP.
- More waste detectors (over-provisioned instances, unused load balancers), each
  with its mandatory discrimination pair.
- Fenced LLM narration of a finding — never in the estimate/category trust path.
