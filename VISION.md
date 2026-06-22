# VISION — Enterprise Security Guardrail Auditor

## 1. One-line statement
A compliance-focused auditor that turns Infrastructure-as-Code (Terraform &
CloudFormation) into an auditable, control-mapped 0–100 Risk Score, caught
pre-deployment — shift-left compliance.

## 2. Problem
Cloud misconfiguration is a leading cause of breaches. Risky patterns — public
S3 buckets, SSH open to `0.0.0.0/0`, unencrypted storage — are introduced in
config files long before they reach a live account. Manual review does not
scale, and security teams need findings expressed in the language of their
audits (CIS, SOC 2, ISO 27001, GDPR), not raw line numbers. The cheapest place
to catch a compliance failure is in the pull request, not in production.

## 3. Who it serves
- **Security / AppSec engineers** — catch high-risk IaC before merge.
- **GRC / compliance** — evidence mapped to named controls for audit.
- **Platform / DevOps teams** — a fast local gate needing no cloud credentials.

## 4. What it does (in scope)
- Parses **Terraform** (HCL) and **CloudFormation** (YAML/JSON) **statically** —
  no `plan`, no `apply`, no live cloud calls.
- Flags **high-risk patterns** via a deterministic rule set. Seed rules:
  public S3 bucket, open SSH (`0.0.0.0/0` → port 22), and a growing baseline.
- For each finding: **explains** the risk and **maps it to a named control**
  (CIS / SOC 2 / ISO 27001 / GDPR).
- Aggregates findings into a **0–100 Risk Score** (severity-weighted) with a grade.
- Exposes a **documented REST API** (API-first) and a **visual dashboard**.
- Accepts input through one **ConfigSource** abstraction:
  - **Uploaded files** — the always-works baseline.
  - **Public repo URL** — shallow, read-only clone, **https-only**, restricted to
    an **exact-match host allowlist**. No private-repo tokens in this build.

## 5. Explicitly out of scope (non-goals)
- No live cloud connection, no credential use, no `terraform`/AWS API calls.
- No auto-remediation or writing back to user files.
- No private-repo authentication / tokens.
- No multi-tenant accounts, RBAC, or SSO.
- **No LLM in the trust path**: the audit and scoring path consumes no model
  output; any LLM is fenced to optional narration and cannot introduce, remove,
  or alter a finding or the score (see Principle 1).

## 6. MVP success criteria
1. Runs end-to-end with **no API key** and **no cloud access**.
2. Catches the named high-risk patterns (public S3, open SSH) in real fixtures,
   AND does not flag safe look-alikes.
3. Maps each finding to a named compliance control.
4. Produces a 0–100 Risk Score visible on the dashboard.
5. REST API is documented (OpenAPI) and exercisable.
6. Deterministic: same input → same score, every run.

## 7. Guiding principles (mandatory)
1. **Deterministic trust path; AI fenced out of it.** The scoring/audit path is
   fully deterministic and runs with no API key. An LLM is an *optional
   accelerant for narration only* — never the authority. It is fenced out of the
   audit path and can never introduce, change, or suppress a finding or the
   score. Removing the LLM changes wording, never verdicts.
2. **Every detector is proven by adversarial evidence.** Each detector ships
   with a matched pair: a test proving it catches a real violation, and a test
   proving it ignores a safe look-alike. No detector ships without both.
3. **The method generalizes.** How findings are detected, proven (adversarial
   pairs), and mapped to named controls is designed to extend to other
   infrastructure-governance domains beyond this single tool — not hard-wired to
   two rules.
4. **Explain, don't just flag.** Every finding carries a plain-language *why*
   plus its named control mapping.
5. **Safe by construction.** Static analysis only; any network access is
   https-only, host-allowlisted, read-only, and never authenticated.
6. **API-first.** The dashboard is just one client of the same documented REST
   API any system can call.
