# ADAPTER — Module-Specific Clauses

The two clauses that bind PROTOCOL.md's generic method to THIS module. No method
content here.

## 1. Domain layer (universal shape)
`finding → named compliance control → Risk Score`

- Every finding maps to a NAMED compliance control drawn from
  **CIS / SOC 2 / ISO 27001 / GDPR**, carrying a **reference URL** for that control.
- Findings aggregate, severity-weighted, into a **0–100 Risk Score**.
- Each finding's explanation is produced by a **DETERMINISTIC template** — this
  is the trust path. Any LLM narration is **OPTIONAL and FENCED**:
  - it may reference ONLY a control already present in the mapping;
  - it can NEVER introduce a new control or change a verdict or the score;
  - if absent or disabled, the deterministic template stands in its place.

## 2. L3 false-positive trap (the discrimination pair)
- **TRUE-POSITIVE — MUST flag:** a bucket made public via policy.
- **NEAR-MISS — MUST NOT flag:** a private bucket with versioning enabled.
