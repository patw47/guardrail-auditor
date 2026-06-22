# EPIC — P3 SRE: Observability & Event Watchdog

> **Honesty line.** This is a **ready-to-execute SPECIFICATION, not a built
> module** — no code, no scaffold here. It is driven by the **same approved
> `PROTOCOL.md`** as P2 (the orchestration method is project-agnostic by design);
> only `ADAPTER.md`'s two clauses change. **No invented metrics** — the
> `Health Score` and error-budget figures are values the tool would *compute*
> from ingested logs, not benchmarks claimed here.

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
| **P3 (this)** | anomaly → SLO / error-budget impact → **Health Score** | a real 10× error spike fires the webhook; a benign burst **doesn't** |

**Identical across all three modules:** detector → discrimination pair · the
deterministic aggregate score · map-to-named-taxonomy + explanation · assurance
(coverage matrix + external oracle). That is what makes three projects *one
method*.

## 2. ADAPTER — the 2 clauses (this is the whole module-specific delta)

**Clause 1 — domain layer (universal shape):**
`anomaly → SLO / error-budget impact → Health Score`
- Every anomaly maps to a **named SLO** and its **error-budget burn**, and
  carries a **deterministic Health Score impact**.
- Anomalies aggregate into a **0–100 Health Score** (the analogue of the Risk
  Score). Explanation is a deterministic template; any LLM narration is fenced
  out of the anomaly/score/alert trust path.

**Clause 2 — L3 false-positive trap (the domain discriminator):**
- **TRUE-POSITIVE — MUST fire the webhook:** a real error spike (e.g. ≥10×
  baseline error rate).
- **NEAR-MISS — MUST NOT fire (no false paging):** a benign traffic burst — a
  deploy blip or an expected hourly peak — where errors stay at baseline.

## 3. Vision (brief)

- **What/why:** parse app/platform logs, detect anomalies/error spikes, fire a
  **simulated** webhook alert, and visualize health trends — SRE signal without
  alert fatigue.
- **In scope:** static analysis of log files/streams (offline); deterministic
  anomaly detectors + Health Score; SLO/error-budget mapping; a simulated webhook
  trigger; a trends dashboard; REST API.
- **Out of scope:** no live ingestion pipeline, no real paging integration (the
  webhook is simulated/recorded, never a real page), no API key for the core.
- **MVP success:** runs offline; fires on a real 10× spike and **stays silent**
  on a benign burst (no false paging); computes the Health Score; records the
  webhook; dashboard shows the trend; deterministic.

## 4. Sprint decomposition

Cross-cutting (per PROTOCOL): **L1** lint+type+tests every sprint · **L2**
VERIFIER conformance · **L3** discrimination pair per detector. Two gates per
sprint. MVP boundary = the dashboard (S7); assurance (S8) is the post-MVP
differentiator.

- **S0 — Scaffold + governance-on-disk.** Goal: project tree, the reused
  governance files written verbatim (PROTOCOL/CLAUDE/verifier) + the swapped
  ADAPTER, FastAPI/SQLite skeleton, CI. *Deps: —.* Accept: L1 green; `/health`
  200; governance files on disk; CI runs the ladder.
- **S1 — Log ingest / parse.** Goal: parse app/platform logs into normalized
  `LogEvent`s + a per-window metric series (error rate, latency). *Deps: S0.*
  Accept: real log fixtures parse into events + windows; malformed lines handled
  cleanly; multiple formats tested.
- **S2 — Anomaly detectors [first L3 sprint].** *(full ticket shape below.)*
- **S3 — Health Score.** Goal: a pure function `anomalies → 0–100 Health Score`
  weighted by SLO/error-budget impact. *Deps: S2.* Accept: same input → same
  score (determinism); no anomalies → 100 (healthy); edge cases covered;
  per-anomaly breakdown returned.
- **S4 — SLO / error-budget mapping + explanation.** Goal: `anomaly → named SLO
  + budget-burn` via a deterministic table + a pure `render()`. *Deps: S3.*
  Accept: every anomaly maps to ≥1 named SLO; render pure; no SLO outside the
  table (fence test).
- **S5 — Webhook alert.** Goal: fire a **simulated** webhook on a real anomaly;
  **idempotent**, gated on the discrimination result so a benign burst never
  pages. *Deps: S4.* Accept: a real spike records exactly one webhook payload; a
  benign burst records **none**; re-runs don't duplicate; the webhook is
  simulated/recorded, never a real call — asserted.
- **S6 — REST API + persistence + log-ingest ConfigSource.** Goal: wire the
  pipeline behind REST, persist a run (schema = sensitive gate). *Deps: S5.*
  Accept: POST logs → 201 with anomalies + Health Score; write→read round-trip
  identical; OpenAPI documents every endpoint.
- **S7 — Trends dashboard. ← MVP COMPLETE.** Goal: a FastAPI-served dashboard
  (API-only): Health-Score gauge + an error-rate / error-budget timeline +
  anomaly table (SLO, budget burn, webhook status) + empty/error states. *Deps:
  S6.* Accept: renders a run from the API; no API key; behavioral/integration
  test.
- **S8 — Assurance (post-MVP differentiator).** Goal: coverage matrix from the CI
  discrimination tests + an external oracle (labelled incident fixtures or a
  reference anomaly detector), **K→K agreement** on the implemented subset.
  *Deps: S2 + S6.* Accept: matrix lists every detector's TP+near-miss verdict
  (CI-sourced); oracle agreement recorded with pinned reference; divergences →
  LIMITATIONS.md (labelled WIN vs limitation); completeness stated honestly.

### S2 ticket — Anomaly detectors (build-ready, P2-S2 shape)
- **Goal:** a deterministic detector engine over the metric series → anomalies,
  with the detectors: **error-rate spike** + **latency regression** (must-have);
  **log-volume drop** + **new-error-signature** (amplification). Each maps the
  supported log/metric shapes onto one rule.
- **Context:** consumes S1's `LogEvent` + windows; `rule_id` is the S4 SLO join
  key; the anomaly carries the baseline + observed values that justified it.
- **Constraints:** detect-only (no scoring/mapping/alert/persistence); no new
  dependency; engine deterministic (sorted output); **every shipped detector has
  BOTH tests** — never a detector without its FP-trap.
- **Eject rule:** if long, ship the 2 must-haves green WITH their discrimination
  pairs and record the other 2 as next-up.
- **Done-when (validation commands pass + criteria met):**
  1. `ruff` / `mypy` / `pytest` green.
  2. **Per detector, the discrimination pair exists as committed CI tests:** a
     true-positive fixture makes exactly that detector fire (correct
     rule/window/baseline) **AND** a near-miss fixture makes it stay silent.
  3. **Clause-2 trap, verbatim, as CI tests:** a ≥10× error spike **fires**; a
     benign burst (deploy blip / hourly peak at baseline error rate) **stays
     silent** — no false paging.
  4. Engine deterministic: shuffled window order → identical ordered anomalies.
  5. A multi-anomaly fixture → all expected anomalies, each carrying its SLO key
     + baseline/observed values.

## 5. Roadmap / out of scope
- Real ingestion source behind the same `ConfigSource` (tail a file / read a
  bucket, safety-guarded — the SSRF analogue). Post-MVP.
- More anomaly detectors (saturation, dependency-failure correlation), each with
  its mandatory discrimination pair.
- Fenced LLM narration of an incident — never in the anomaly/score/alert trust
  path.
