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
