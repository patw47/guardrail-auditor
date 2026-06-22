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

## S1
- **Parsers live in `core/parsing/`** (ingest = front of the pipeline, in the
  core data layer). Public API: `parse_file(path)`, `parse_content(content,
  filename)`, `ParseError`. Dispatch by extension: `.tf`→Terraform;
  `.yaml/.yml/.json/.template`→CloudFormation.
- **`Resource`** (`models/resource.py`) is the single normalized type both
  formats converge on: `format`, `type` (native string), `name`/logical-id,
  `attributes` (dict), `file`, `line`.
- **hcl2 v8 reality** (probed before coding): blocks are ALWAYS lists tagged
  `__is_block__` (marker stripped by the mapper) — so a nested block is always a
  list, len 1 for a single occurrence; scalar strings are quote-wrapped (mapper
  unquotes). `with_meta` is gone in v8 → **TF line numbers come from a
  comment-stripped header line-scan** (`_header_lines`), provably robust to
  leading comments.
- **CFN**: a `yaml.SafeLoader` subclass + `add_multi_constructor("!", …)` turns
  intrinsic tags into marker dicts (`!Ref X`→`{"Ref":"X"}`, `!Foo`→`{"Fn::Foo":…}`);
  per-resource line from the `yaml.compose` node tree; JSON rides the same path.
- **`.tf.json` deferred** (TF-first = HCL); `.json` currently routes to CFN.
- **For S2 detectors**: read normalized resources. TF security-group ingress is
  at `attributes["ingress"]` (list of dicts, `cidr_blocks` list of unquoted
  strings); CFN is `attributes["SecurityGroupIngress"]` (list) with `CidrIp`.
  Public-bucket signals differ too (TF `acl`/policy vs CFN `AccessControl`).
  Detectors must map BOTH native shapes onto each rule.

## S2
- **`rule_id` is the stable join key** for the S4 control mapping; `Finding`
  carries `severity` (for the S3 score) but no control/score yet.
- **Severities anchored to a citable authority and VERIFIED against the source
  page/rego** (not asserted) so the S3 score weights and the S4 mapping draw on
  the SAME source and survive the S7 Checkov/TerraGoat oracle (K→K). Verified
  values (source = current `aquasecurity/trivy-checks` main rego, cross-read vs
  the AVD pages):
  | rule_id | severity | source (verified) | CIS AWS |
  |---------|----------|-------------------|---------|
  | `OPEN_SSH` | **critical** | AVD-AWS-0107 page = CRITICAL (search-confirmed). NOTE: current `ec2/no_public_ingress_sgr.rego` = HIGH (drift); kept CRITICAL per the AVD page + architect hardening #1 | 5.2 |
  | `PUBLIC_DB` | **high** | `rds/disable_public_access.rego` severity: HIGH (corrected from critical — the legacy tfsec doc page said critical, stale; current rego = HIGH) | — |
  | `S3_PUBLIC_BUCKET` | **high** | `s3/no_public_access_with_acl.rego` severity: HIGH | 2.1.5 |
  | `UNENCRYPTED_STORAGE` | **high** | `ec2/enable_volume_encryption.rego` + `rds/encrypt_instance_storage_data.rego` severity: HIGH | 2.2.1 |
  Reconciliation: only `OPEN_SSH` is CRITICAL (per AVD-AWS-0107 + hardening #1);
  the other three are HIGH per their current rego. `PUBLIC_DB` was lowered
  critical→high during the Gate-S2 source-check. These IDs are the S4 seeds.
- **GOVERNING RULE (binds S4):** each detector's `severity` MUST equal what its
  own `reference_url` page states — the dashboard's cited authority and the
  assigned severity can never contradict. S4 must set each `reference_url` to a
  page whose stated severity matches: OPEN_SSH→AVD-AWS-0107 (Critical);
  S3_PUBLIC_BUCKET→S3 no-public-access-with-acl (High); UNENCRYPTED_STORAGE→
  EBS enable-volume-encryption / RDS encrypt-instance-storage-data (High);
  PUBLIC_DB→RDS disable-public-access (High).
- **OPEN_SSH ruling (architect): keep CRITICAL.** AVD-page-vs-current-rego drift
  is recorded in `LIMITATIONS.md`, not hidden.

## S3
- **Risk Score = pure deterministic aggregation** (`core/scoring.py`,
  `score_findings(findings) -> Score`). Higher = worse; 0 = clean. No I/O/LLM.
- **Severity weights** (additive, then `min(100, Σ)`): `critical=50, high=15,
  medium=5, low=1`. Tuned so ONE critical (50) > TWO highs (30) — keeps the
  OPEN_SSH=critical decision meaningful, not flattened.
- **Grade bands (numeric):** `0→A · 1–19→B · 20–39→C · 40–69→D · 70–100→F`.
- **Severity floor (couples grade to worst severity, not just the sum):** any
  `critical` ⇒ grade ≤ **D**; else any `high` ⇒ grade ≤ **C**. Final grade =
  the WORSE of the numeric band and the floor (a lone high → C, a lone critical
  → D; the floor only worsens, never improves a worse numeric grade).
- **Breakdown** = one `ScoreItem` per finding (rule_id, severity, resource,
  file, line, weight), ordered `(severity_rank, rule_id, file, line)` for
  determinism. `Score.counts` = findings per severity.

## S4
- **Compliance mapping** in `core/compliance.py`: `map_finding(finding) ->
  list[Control]` via the static `CONTROL_MAP` keyed by `rule_id`; pure
  `render(finding) -> str`. **No LLM, no runtime network** (URLs are static).
- **`Framework` = CIS / SOC2 / ISO27001 / GDPR only.** AVD is NOT a framework —
  it lives in a separate `AVD_ANCHOR` table (severity provenance) used by the
  governing-rule test, never rendered as a compliance control.
- **Verified control ids** (pinned **CIS AWS v3.0.0**, **ISO 27001:2022**,
  **SOC 2 TSC CC6.1**, **GDPR Art. 32**): OPEN_SSH→CIS §5.2 + SOC2 CC6.1 + ISO
  A.8.20; S3_PUBLIC_BUCKET→CIS §2.1.4 + SOC2 CC6.1 + ISO A.5.15 + GDPR Art.32;
  UNENCRYPTED_STORAGE→CIS §2.2.1 + ISO A.8.24 + GDPR Art.32; PUBLIC_DB→ISO A.8.20
  (primary) + CIS §2.3 (section-level, see [[LIMITATIONS]]).
- **Precision is visible:** `Control.level` ∈ {precise, section}; a section cite
  renders as `§2.3 (section)` so it can't be mistaken for a precise control.
- **Governing rule (S2) bound:** `AVD_ANCHOR[rule_id].severity == RULES[rule_id]`
  severity — cited source and severity agree. Tested.
- **ADAPTER §1 fence:** `map_finding` only returns controls in `CONTROL_MAP`;
  unknown rule_id → `[]`; mapping never alters a finding/score. Tested.

## S5
- **`ConfigSource` protocol** (`core/config_source.py`): `iter_files() ->
  Iterable[(filename, content)]` + `source_type`. S5 ships `UploadedFilesSource`
  only; **S5b adds `RepoUrlSource` behind the same protocol** (no API change).
- **`run_scan(source) -> ScanResult`** (`core/pipeline.py`) is the single
  pipeline entry: parse→detect→score→map→render. `ScanResult` mirrors the
  persisted shape (ScoreSummary + MappedFinding[]), so the round-trip can compare
  persisted-vs-pipeline by `==`.
- **Schema** (4 tables) in `core/tables.py`, separate from pure `models/`; the
  **repository** (`core/repository.py`) maps domain↔ORM. `explanation` + `weight`
  denormalized onto findings (dashboard reads them directly).
- **`DATABASE_URL` env var** (default `sqlite:///./guardrail.db`) — tests set it
  to a temp file in `conftest.py` BEFORE importing `core.db`, isolating the DB.
- **API is a thin client of the pure pipeline** — routes persist a `run_scan`
  result and serve it back; OpenAPI auto-documents every endpoint via the
  `api/schemas.py` Pydantic response models. S6 dashboard consumes this same API.

## S6
- **Dashboard** = static `web/index.html` + `web/static/{app.js,styles.css}`,
  served by FastAPI (`GET "/"` + `/static` mount), **consuming `/api` only** —
  no business logic in JS. Vanilla JS, no framework, no build step, no new dep.
- **`ControlOut.label`** is computed in the API from the domain `Control.label`
  (single source of truth) so the `§…(section)` marker can't drift in the UI.
  Derived, not newly persisted.
- **Severity by colour AND text** (badge text = `SEVERITY.toUpperCase()` + a
  `.sev-*` colour class) — never colour alone (accessibility).
- **Behavioral tests are dep-light** (served page + API contract + JS-wiring
  assertions); the **DOM render is checked by a manual screenshot**
  (`docs/screenshots/dashboard.png`), not Playwright — no browser dep.
- **DEFERRED — Rescan button → S5b.** "Rescan the same source" only makes sense
  for a re-fetchable URL source; for an upload it would mean re-uploading. So the
  Rescan control ships with the repo-URL input at S5b, not here. Recorded
  decision, not an omission.

## S7
- **Two DISTINCT assurance streams** (never conflated):
  - **Part A — coverage matrix** (`docs/coverage_matrix.md`): generated by
    `tools/coverage_matrix.py` from the labelled manifest (`tests/oracle/
    manifest.yaml`) joined to **real `pytest --junitxml` outcomes**. Guard test
    `tests/oracle/test_coverage_matrix.py` enforces completeness + no drift.
  - **Part B — external oracle** (`tests/oracle/`): Checkov 3.2.334 × TerraGoat
    `729f8da…`, run once locally (authorized §c.3), genuine reference committed
    (`checkov_reference.json` + `SOURCES.md`); `test_oracle_agreement.py` compares
    my scanner offline. **K→K agreement** on the implemented subset TerraGoat
    exercises: 3/3 (OPEN_SSH/PUBLIC_DB/UNENCRYPTED_STORAGE). S3_PUBLIC_BUCKET has
    no positive TerraGoat case — stated in [[LIMITATIONS]].
- **Checkov is DEV/CI-only** — `[project.optional-dependencies] oracle`, never a
  runtime dep; CI compares against the committed reference (no network/Checkov).
- **Vendored TerraGoat secrets are `REDACTED-FOR-COMMIT`** (push-protection);
  redaction never touches the attributes detectors read.
- Claim discipline: **"Checkov validates; the copilot differentiates"** — agreement
  on K→K, NOT recall vs all Checkov.

## S5b
- **`RepoUrlSource`** = second `ConfigSource` impl (behind the same protocol, no
  pipeline change). **SSRF-safe by construction:** `validate_repo_url` runs
  BEFORE any clone — https-only, exact-match `ALLOWED_HOSTS = {github.com,
  gitlab.com}` (rejects IP literals, localhost, `github.com.evil.com`, userinfo).
  Clone is `git clone --depth 1 --no-tags`, `GIT_TERMINAL_PROMPT=0`, temp dir,
  **never apply**, **cleanup in try/finally** (even on error). `cloner` injectable
  → CI offline; one real clone verified locally.
- **`run_scan(source, strict=True)`** — uploads strict (malformed → 400); repo
  scans `strict=False` (skip non-standalone fragments).
- **Schema:** nullable `source_ref` on `scans` (repo_url for repo scans, NULL for
  uploads) → enables Rescan. **Rescan:** repo → new scan; upload → **409** (an
  upload genuinely isn't re-fetchable).
- **Endpoints:** `POST /api/scans/repo` {repo_url}, `POST /api/scans/{id}/rescan`.
  Dashboard adds a repo-URL input + Rescan (shown only when source_type=repo_url),
  still `/api`-only. **No new runtime dep** (git is a system tool).
- Roadmap: more allowlist hosts (Bitbucket), per-file parse-tolerance nuances.

## S8
- **Remediation** (`core/remediation.py`, `models/remediation.py`): pure data,
  keyed by the SAME `rule_id` as `CONTROL_MAP`; each summary cites the same
  control the finding maps to (§5.2 / §2.1.4 / §2.2.1 / A.8.20). Exposed via a
  **computed** `FindingOut.remediation` (derived from rule_id, like the control
  label) — **no schema change**. `remediate()` is fenced (unknown rule → None).
- **README** is guarded by `tests/test_readme.py` — it must name real commands/
  endpoints and reference files that exist (no lying README).
- **`tools/demo_seed.py`**: offline (bundled fixtures), **idempotent** via a
  `source_ref="__demo__"` tag (re-run replaces, never piles up). `*.db` gitignored.
- **`tools/` is a package** (`__init__.py`) so mypy doesn't see `demo_seed` under
  two module names once it's imported in a test.
- **PLAN COMPLETE: S0–S8.** Scaffold → parsers → detectors (L3) → Risk Score →
  compliance mapping → API + persistence → dashboard → assurance (matrix +
  oracle) → repo-URL/SSRF + Rescan → remediation + README.
- **Public-via-policy detection** keys on a statement with `Effect: Allow` + a
  wildcard `Principal` AND **no scoping `Condition`** — a `Condition`
  (e.g. `aws:SourceIp`/`aws:SourceVpce`) means NOT public. This is the exact
  Checkov false positive we deliberately stay silent on (`s3_policy_conditioned.tf`).
- **Detectors are detect-only**; engine output sorted by `(file, line, rule_id)`
  for determinism. Scoring is S3, mapping is S4.
