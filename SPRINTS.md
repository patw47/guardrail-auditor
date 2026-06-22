# SPRINTS.md — Decomposition (Global Deliverable)  [rev 3 — LOCKED at Gate 1]

Target: a static Terraform/CloudFormation auditor — API-first on SQLite,
deterministic core, no API key — that flags high-risk patterns, maps each
finding to a named compliance control (CIS/SOC 2/ISO 27001/GDPR) with a
reference URL, aggregates a 0–100 Risk Score, and shows it on a dashboard.

Cross-cutting per PROTOCOL.md (every sprint): L1 lint+type+tests green;
L2 VERIFIER conformance audit; L3 adversarial discrimination pair on any sprint
that adds a detector. Entities accrete with the domain (resource@parse,
finding@detect, score@aggregate, control@map); SQLite is a thin layer from the
scaffold, concrete tables + first full-scan persistence at S5. One commit per
sprint after the evidence gate.

Dependency chain:
  S0 → S1 → S2 → S3 → S4 → S5 → S5b → S6   ← MVP boundary (scaffold → dashboard)
                          S5 ↘ S7 (assurance: needs S2 + S5, NOT S5b)
                                         S6 ↘ S8 (polish)
Roadmap (not planned sprints): fenced LLM narration; further detector baseline.

═══════════════════════════════════════════════════════════════════════
## MVP  (S0–S6)
═══════════════════════════════════════════════════════════════════════

### S0 — Scaffold, governance-on-disk, CI   [greenfield]
- **Goal:** Project tree + the 5 LOCKED governance files written to disk exactly
  as approved (no redraft) + memory/highlights stubs + a FastAPI skeleton
  (boots, `/health` 200) + a THIN SQLite layer (engine/session/init; tables
  accrete later) + tooling (ruff/mypy/pytest) + CI.
- **Depends-on:** —
- **Acceptance:**
  - `ruff check .`, `mypy .`, `pytest -q` all green.
  - App boots; `GET /health` → 200.
  - VISION/PROTOCOL/ADAPTER/CLAUDE/.claude/agents/verifier.md present on disk,
    byte-for-byte as approved; memory/{decisions,lessons}.md + highlights.md exist.
  - CI runs lint+type+tests on push (workflow file present).

### S1 — Ingest: parsers → normalized resource model
- **Goal:** Parse Terraform (HCL) and CloudFormation (YAML/JSON) into ONE
  normalized resource model (`type`, `name`, `attributes`, source `file`+`line`).
  Defines the **resource** domain type. (How bytes arrive = ConfigSource, lands
  at S5; this sprint takes file content/paths.)
- **Depends-on:** S0
- **Acceptance:**
  - Fixtures of both formats parse into normalized resources with correct
    file/line refs.
  - Malformed input rejected cleanly (no crash, clear error).
  - Tests cover both formats + the malformed case.

### S2 — Detector engine + detectors (2 must-have + 2 amplification)  [L3]
- **Goal:** Detector interface + engine over normalized resources → findings
  (severity, resource ref, file/line, evidence). Defines the **finding** domain
  type. Gated core: **public S3 bucket**, **open SSH (0.0.0.0/0 → 22)**.
  In-sprint amplification: **unencrypted storage**, **publicly-accessible DB**.
- **Depends-on:** S1
- **Eject rule:** if the sprint runs long, ship the 2 must-haves green WITH their
  discrimination pairs and record the other 2 as next-up — never a detector
  without its FP-trap test.
- **Acceptance (L3 discrimination pair per detector — TP MUST fire, near-miss
  MUST NOT):**
  - public-via-policy bucket flags; private bucket w/ versioning does not (ADAPTER §2).
  - SSH 0.0.0.0/0→22 flags; SSH on restricted CIDR / non-22 port does not.
  - unencrypted storage flags; encrypted look-alike does not.
  - publicly-accessible DB flags; private DB look-alike does not.
  - Engine deterministic; every shipped detector has both tests; all green.

### S3 — Risk Score (pure deterministic aggregation)
- **Goal:** A pure function: findings → severity-weighted **0–100 Risk Score** +
  letter grade + the **per-finding breakdown** (not just a number). Defines the
  **score** domain type. No I/O, no LLM.
- **Depends-on:** S2
- **Acceptance:**
  - Same input → identical score+grade every run (determinism unit test).
  - Edge cases: **no findings → 0**; **all-critical → capped at 100**.
  - Returns the per-finding contribution breakdown; weighting + grade boundaries
    unit-tested.

### S4 — Compliance mapping + deterministic explanation  [differentiator]
- **Goal:** `finding → named control` (CIS/SOC 2/ISO 27001/GDPR) + `reference_url`
  via a deterministic table; a pure `render()` NL-explanation template per
  finding. Defines the **control mapping** domain type. **No LLM** (ADAPTER §1).
- **Depends-on:** S3
- **Acceptance:**
  - Each seed finding maps to ≥1 named control with a real `reference_url`.
  - `render()` is pure: same finding → same explanation text; no model call.
  - Table + render covered by tests; no `control_id` outside the mapping can appear.

### S5 — REST API + uploaded-files ConfigSource + persistence
- **Goal:** Wire the pipeline behind REST and persist a scan. The `ConfigSource`
  abstraction with its **uploaded-files** implementation only. Concrete SQLite
  tables (Scan/Finding/Score/Control). Endpoints: `POST /scans` (uploaded files)
  runs ingest→detect→score→map→persist + returns id/summary; `GET /scans`,
  `GET /scans/{id}`, `GET /scans/{id}/findings`, `GET /scans/{id}/score`. OpenAPI
  at `/docs`. First full-scan persistence happens here.
- **Depends-on:** S4
- **Sensitive gate (§c.3) — ONE, surfaced at the start gate before any code:**
  the **persistence / DB schema** (concrete SQLite tables for Scan/Finding/
  Score/Control).
- **Acceptance:**
  - POST (uploaded files) → findings+score persisted and returned.
  - **Round-trip:** a Scan with its Findings + Score writes→reads back identical.
  - OpenAPI documents every endpoint; integration tests cover happy + bad-input.

### S5b — public-repo-URL ConfigSource   [security feature, isolated]
- **Goal:** Add the second `ConfigSource` implementation ONLY: a **public-repo-URL**
  shallow, read-only clone, behind the same abstraction; scan the clone through
  the existing S5 pipeline.
- **Depends-on:** S5
- **Sensitive gate (§c.3) — ONE, surfaced at the start gate before any code:**
  the **network clone** — SSRF-safe by construction: **https only**, **exact-match
  host allowlist**, read-only, no tokens.
- **Acceptance:**
  - **SSRF discrimination test:** a non-allowlisted host (`169.254.169.254`,
    `localhost`) is REJECTED; an allowlisted https host is accepted.
  - **Parity test:** the same files via upload vs via `repo_url` → identical
    findings + score.

### S6 — Dashboard (visual Risk Score)   ← MVP COMPLETE
- **Goal:** Static dashboard served by FastAPI: submit files OR paste a public
  repo URL → Risk Score gauge + grade, findings table (control mapping +
  explanation), severity breakdown chart. Client of the REST API only.
- **Depends-on:** S5b
- **Acceptance:**
  - Dashboard renders a scan's score + findings from the API.
  - Headline demo works: paste public repo URL → Risk Score.
  - Loads and runs with **no API key**; a behavioral/integration test drives
    submit → score visible.

═══════════════════════════════════════════════════════════════════════
## Post-MVP  (S7 differentiator, S8 polish)
═══════════════════════════════════════════════════════════════════════

### S7 — Adversarial assurance: coverage matrix + external oracle
- **Goal:** Publish functional assurance. (a) Collect every detector's TP +
  FP-trap verdict into ONE `rule → case → verdict` artifact, **built from the CI
  tests already written in their sprints** (not re-run by hand), cross-checked
  against a labelled fixture manifest. (b) External oracle: **Checkov on
  TerraGoat**, pinned version + commit, reference committed under
  `tests/oracle/`; claim = **agreement on my implemented subset (K→K)**, NOT
  recall vs all Checkov.
- **Depends-on:** S2 (detectors/tests) + S5 (pipeline/persistence) — NOT S5b.
- **Acceptance:**
  - Coverage matrix lists every detector with TP + FP-trap verdict, sourced from
    CI test results; cross-checked vs the labelled manifest; no manual re-run.
  - Checkov pinned (version+commit) reference committed in `tests/oracle/`;
    agreement on the implemented subset (K→K) reported as **agreement, not recall**.

### S8 — Final polish: remediation + README/docs
- **Goal:** Per-finding **remediation** (a corrected IaC snippet / CLI action);
  README + quickstart; OpenAPI examples; a demo seed that populates a
  representative dashboard. (Remediation + README live HERE, not scattered.)
- **Depends-on:** S6
- **Acceptance:**
  - Each finding type carries a remediation snippet/action, covered by a test.
  - README quickstart runs end-to-end; demo produces a populated dashboard.

═══════════════════════════════════════════════════════════════════════
## Roadmap (NOT planned sprints)
═══════════════════════════════════════════════════════════════════════
- **Fenced LLM narration** — narration only, never in the trust path; MVP runs
  with no API key. If built later it carries a fence test: verdict + Risk Score
  **byte-identical LLM-on vs LLM-off**, plus a post-check rejecting any
  `control_id` outside the mapping.
- **Detector baseline growth** — more high-risk patterns, each with its
  mandatory discrimination pair.

═══════════════════════════════════════════════════════════════════════
MVP = S0–S6 (scaffold → dashboard, headline "paste repo URL → Risk Score").
Sensitive gates: S5 (persistence/schema), S5b (network clone); any future
LLM/secret work (roadmap). Sprints never chain — Gate 2(a) at start, Gate 2(b)
on evidence, each sprint.
═══════════════════════════════════════════════════════════════════════
