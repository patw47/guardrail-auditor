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
