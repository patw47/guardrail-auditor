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

## Deferrals (roadmap)
- **S3 server-side-encryption absence:** `UNENCRYPTED_STORAGE` is scoped to an
  explicit `encrypted=false` on EBS/RDS only; SSE-absent buckets are noisier and
  deferred.
- **`.tf.json`** (Terraform JSON syntax): deferred at S1 (TF-first = HCL).
- **Heredoc-body normalization in the S1 parser:** hcl2 returns heredocs wrapped
  in `<<TAG`…`TAG`; currently handled detector-local via `_strip_heredoc`.
  Normalizing in the parser (so no consumer sees the markers) is a roadmap item.
