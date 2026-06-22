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
- **Public-via-policy detection** keys on a statement with `Effect: Allow` + a
  wildcard `Principal` AND **no scoping `Condition`** — a `Condition`
  (e.g. `aws:SourceIp`/`aws:SourceVpce`) means NOT public. This is the exact
  Checkov false positive we deliberately stay silent on (`s3_policy_conditioned.tf`).
- **Detectors are detect-only**; engine output sorted by `(file, line, rule_id)`
  for determinism. Scoring is S3, mapping is S4.
