# LIMITATIONS & Adjudications

Known limitations, deferrals, and source-conflict adjudications — shown, not hidden.

## Severity source conflicts

### OPEN_SSH — AVD page (CRITICAL) vs current trivy-checks rego (HIGH)
- **Detector:** `OPEN_SSH` — security-group ingress permitting SSH (TCP 22) from
  `0.0.0.0/0`.
- **Conflict:** the published AVD page **AVD-AWS-0107** states **Critical**; the
  current `aquasecurity/trivy-checks` main `ec2/no_public_ingress_sgr.rego`
  metadata states **HIGH**.
- **Adjudication: CRITICAL.** Governing rule — a detector's severity must equal
  what its own `reference_url` page states. `OPEN_SSH`'s `reference_url` points at
  the AVD-AWS-0107 page (Critical), so the dashboard's cited authority and the
  assigned severity agree; otherwise the tool would contradict its own source.
  Also matches the merits (unauthenticated SSH from `0.0.0.0/0` is textbook
  critical) and gives the Risk Score a real spread (1 critical / 3 high) rather
  than flat weights. Revisit if the AVD page itself is reclassified.
- **Corrected in the same source-check:** `PUBLIC_DB` was lowered critical→high —
  the current `rds/disable_public_access.rego` says HIGH (the legacy tfsec doc
  page's "critical" is stale drift).

## Compliance-mapping provenance

### PUBLIC_DB → CIS: precise sub-number unverified, cited at section level
- The CIS AWS Foundations Benchmark **v3.0.0** RDS-public-access control could
  not be verified to a precise sub-number from an authoritative source (search
  surfaced AWS Security Hub's `RDS.2`, which is not a CIS number). Rather than
  guess `2.3.3`, `PUBLIC_DB` cites **CIS §2.3 (RDS section)** marked
  `level="section"`, rendered visibly as `§2.3 (section)`. Its **primary** named
  control is **ISO 27001:2022 A.8.20** (verified). Surfaced, not hidden.
- All other CIS ids verified against v3.0.0: SSH **§5.2**, S3 BPA **§2.1.4**
  (drift from v1.4's 2.1.5), EBS encryption **§2.2.1**.

## External oracle (Checkov × TerraGoat) — completeness + divergences

Evidence stream **B**, distinct from the Part-A coverage matrix. Checkov 3.2.334
on TerraGoat @ `729f8da…`, read-only static (see `tests/oracle/SOURCES.md`).

### Completeness — which rules TerraGoat actually exercises (K→K only)
- **Positively exercised** (a positive case + a matching Checkov check) —
  **agreement 3/3**: `OPEN_SSH` (CKV_AWS_24), `PUBLIC_DB` (CKV_AWS_17),
  `UNENCRYPTED_STORAGE` (CKV_AWS_16), all on `aws_security_group.web-node` /
  `aws_db_instance.default`.
- **Not positively exercised:** `S3_PUBLIC_BUCKET` — TerraGoat has no
  public-via-ACL/policy bucket; my tool AND Checkov's CKV_AWS_20 are both clear
  (consistent, but **no positive oracle confirmation**). Stated, not hidden.

### Divergences (labelled; never silently reconciled)
- **TYPE (b) — honest limitation / scope:** Checkov flags **CKV2_AWS_6**
  (S3 *block-public-access*) on 6 buckets; my tool does **not** implement that
  check (I scope S3 to public-via-ACL/policy). A breadth limitation, not a
  correctness miss on a shared check — Checkov validates breadth; the copilot
  differentiates with control-mapping + explanation on its implemented subset.
- **TYPE (a) — WIN:** none on TerraGoat (no wildcard+`Condition` bucket present).
  The stricter-and-correct WIN (staying silent on the exact Checkov-style false
  positive) is demonstrated on the project's own corpus in the **Part-A matrix**
  (`s3_policy_conditioned.tf`), kept DISTINCT from this oracle stream.

## Deferrals (roadmap)
- **S3 server-side-encryption absence:** `UNENCRYPTED_STORAGE` is scoped to an
  explicit `encrypted=false` on EBS/RDS only; SSE-absent buckets are noisier and
  deferred.
- **`.tf.json`** (Terraform JSON syntax): deferred at S1 (TF-first = HCL).
- **Heredoc-body normalization in the S1 parser:** hcl2 returns heredocs wrapped
  in `<<TAG`…`TAG`; currently handled detector-local via `_strip_heredoc`.
  Normalizing in the parser (so no consumer sees the markers) is a roadmap item.
