# Highlights — deck material (write-only, never re-injected)

## Trigger legend
CATCH · DISCRIMINATION · GATE · DECISION · GENERALITY · MAPPING · METRIC

## Seeded (foundational)
- **ASSURANCE** — validation runs in an independent read-only agent (separate
  context window, Read/Grep/Bash only) that reviews the repo artifacts but not
  the BUILDER's conversation or reasoning — structural assurance, not
  self-review.

## S0
- **GATE** — three governance gates (A1/A2/A3) + the plan gate + the S0 start
  gate all cleared on architect review *before any code*; S0 reached its evidence
  gate green (ruff/mypy/pytest all 0).
- **ASSURANCE** (seeded highlight, now live) — the independent read-only VERIFIER
  ran in a separate context (opus; Read/Grep/Bash; no Edit/Write), audited
  delivered-vs-ticket, and returned PASS with "no tampering found" — structural
  assurance demonstrated on the very first sprint.

## S1
- **DECISION** — chose a comment-stripped header line-scan over `python-hcl2`'s
  metadata (which v8 removed) for Terraform line numbers, making finding lines
  *provably* survive leading `#`/`//`/`/* */` comments — the exact silent break
  the architect flagged. Proven by fixtures whose resources sit behind comment
  blocks (public_bucket→line 6, MyBucket→line 7).
- **GENERALITY** — one normalized `Resource` and one `parse_file()` unify
  Terraform HCL and CloudFormation YAML/JSON behind a single ingest API; the
  detector layer (S2) never sees a format quirk (nested blocks always lists,
  scalars unquoted, intrinsics as marker dicts).

## S2
- **DISCRIMINATION** — all 4 detectors are real discriminators: each fires on its
  true-positive and stays silent on a safe look-alike *of the same resource
  type*. The differentiator near-miss: a bucket policy with wildcard
  `Principal:"*"` BUT a scoping `Condition` (source-IP) stays SILENT — the exact
  false positive Checkov trips on — alongside the ADAPTER §2 private+versioning
  near-miss.
- **CATCH** — the L3 true-positive test caught a real bug: hcl2 v8 wraps heredocs
  in `<<TAG`…`TAG`, so the public-via-policy detector silently missed. Fixed
  (`_strip_heredoc`) and re-proven green.
- **GATE** — the independent VERIFIER FAILed S2 even though the detector code was
  correct: hardening H2 required the AVD/CIS severity citation in
  `decisions.md`, which was missing while code already claimed it was documented.
  Doc-only remediation → re-verified PASS. The gate has teeth; it caught a
  real doc/code drift, not a cosmetic nit.

## S3
- **METRIC** — the deterministic Risk Score gives a real spread, not flat
  weights: `multi_violation` (1 critical + 3 high) = **95/100, grade F**;
  no findings = **0/A**; all-critical = **100/F (capped)**. Every number is
  explained by a per-finding breakdown.
- **DECISION** — the grade couples to the *worst severity present*, not just the
  sum: a severity floor (any critical ⇒ ≤ D, any high ⇒ ≤ C) means a lone
  critical can't hide behind an additive total, and weights (1 critical 50 >
  2 highs 30) keep the OPEN_SSH=critical ruling meaningful in the score.

## S4
- **MAPPING** — every finding now carries *verified* named compliance controls +
  a deterministic explanation: e.g. OPEN_SSH → CIS AWS v3.0.0 §5.2 · SOC 2 CC6.1
  · ISO 27001:2022 A.8.20, with real reference URLs. The audit tool speaks the
  auditor's language (CIS / SOC 2 / ISO 27001 / GDPR), no LLM in the path.
- **DECISION** — source-checking the control ids caught a version drift (S3 BPA
  is §2.1.4 in v3.0.0, not v1.4's §2.1.5) and refused to guess the unverifiable
  CIS RDS sub-number — cited §2.3 with a visible `(section)` marker instead. A
  fabricated control id would be the worst credibility hit for an audit tool;
  the marker turns the limitation into a maturity signal.

## S5
- **GATE** — the 4-table schema passed a type-3 sensitive gate *before* any code;
  then the **persisted-vs-pipeline round-trip** proved the API layer didn't drift
  from the deterministic core (VERIFIER's negative control: corrupt a persisted
  value → equality flips). API-first, evidence-backed.
- **GENERALITY** — one `ConfigSource` abstraction and one `run_scan` entry: the
  REST API is a thin client of the same pure pipeline (parse→detect→score→map),
  and the public-repo-URL source (S5b) slots in behind the same protocol with no
  API change. `POST /api/scans` → 201 with a 95/F scored, control-mapped result.

## S6 — MVP CLOSE
- **METRIC** — the whole pipeline now renders end-to-end in a served dashboard:
  upload `multi_violation.tf` → **95/100, grade F** gauge + a findings table
  (severity badge by colour AND text, plain-language explanation, clickable
  control links); a clean file → **0/A** empty state; malformed → error state.
- **MAPPING** — the `§2.3 (section)` honesty marker (born from the S4
  verifier-caught decision) survives all the way to the rendered control link,
  single-source via the API `label` — no JS drift.
- **GATE** — **MVP (S0–S6) closed**: scaffold → parsers → detectors (L3 pairs) →
  Risk Score → compliance mapping → REST API + persistence → dashboard, every
  sprint through a 2-gate loop with an independent read-only VERIFIER.

## S7
- **DISCRIMINATION** — a published **coverage matrix** (`docs/coverage_matrix.md`,
  12 cases, all PASS) proves every detector fires on its TP and stays silent on
  its near-miss, INCLUDING the hard wildcard+`Condition` Checkov-style FP — and
  the verdict column is sourced from **real `pytest --junitxml` output**, not a
  hand-run (guarded against drift).
- **METRIC** — external oracle: **Checkov 3.2.334 × TerraGoat** (pinned), genuine
  reference committed. **K→K agreement 3/3** on the rules TerraGoat exercises
  (OPEN_SSH/PUBLIC_DB/UNENCRYPTED_STORAGE); S3 has no positive case — stated, not
  padded. *"Checkov validates; the copilot differentiates."*
- **GATE** — the VERIFIER independently confirmed the Checkov reference is
  *genuine tool output* (line ranges match the files, verdicts match reality),
  not synthesized — the anti-fabrication bar for an audit tool, met.

## S5b
- **GENERALITY** — the headline *"paste a public repo URL → Risk Score"* works:
  `RepoUrlSource` slots behind the same `ConfigSource` with **zero pipeline
  change**, and a **parity test** proves upload ≡ repo_url (identical findings +
  score). A real TerraGoat clone over https scored **80/F** end-to-end.
- **DECISION** — SSRF-safe **by construction**: `validate_repo_url` runs *before*
  any clone (https-only, exact-match allowlist — rejects `169.254.169.254`,
  `localhost`, `github.com.evil.com`, userinfo), the clone is shallow/read-only/
  never-apply, and the temp dir is cleaned up in `try/finally` even on error.
  Security feature isolated from the schema, CI stays offline via an injectable
  cloner.
