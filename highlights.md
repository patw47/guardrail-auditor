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
