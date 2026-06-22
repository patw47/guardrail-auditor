# Oracle Sources — Checkov × TerraGoat (reproducible)

External reference for the K→K agreement check (evidence stream **B**, distinct
from the Part-A coverage matrix). A ONE-TIME local op (authorized, PROTOCOL §c.3):
shallow read-only clone + Checkov static analysis, **never apply, no live cloud**.
The committed artifacts let CI compare **offline** — no network, no Checkov
dependency in CI.

## Pins
- **TerraGoat** commit `729f8da62c6a85ce4af5ad3d123de97776d954c4`
  (github.com/bridgecrewio/terragoat, Apache-2.0).
- **Checkov** `3.2.334`.

## Reproduce
```
git clone --depth 1 https://github.com/bridgecrewio/terragoat.git
git -C terragoat checkout 729f8da62c6a85ce4af5ad3d123de97776d954c4
python -m venv oracle-venv && ./oracle-venv/bin/pip install checkov==3.2.334
./oracle-venv/bin/checkov -d terragoat/terraform/aws --compact -o json > checkov.json
```

## Committed artifacts
- `checkov_reference.json` — the **genuine** Checkov output (real `CKV_*` ids /
  `check_result` format), filtered to the resources my detectors target + the
  mapped check_ids.
- `terragoat/{ec2,db-app,s3}.tf` — the vendored TerraGoat files my scanner runs
  on (the ones containing my findings). **Note:** TerraGoat ships *deliberate*
  fake secrets; secret-like values in these vendored copies are
  `REDACTED-FOR-COMMIT` (push-protection safety). Redaction touches only
  credential strings — never the attributes my detectors read
  (`publicly_accessible`, `storage_encrypted`, `cidr_blocks`, `acl`).

## rule_id ↔ Checkov check_id (verified from the real output)
| rule_id | Checkov check | TerraGoat verdict |
|---------|---------------|-------------------|
| `OPEN_SSH` | CKV_AWS_24 (SG ingress 0.0.0.0/0 → 22) | both **FAIL** @ aws_security_group.web-node |
| `PUBLIC_DB` | CKV_AWS_17 (RDS publicly accessible) | both **FAIL** @ aws_db_instance.default |
| `UNENCRYPTED_STORAGE` | CKV_AWS_16 (RDS encryption at rest) | both **FAIL** @ aws_db_instance.default |
| `S3_PUBLIC_BUCKET` | CKV_AWS_20 (S3 public-read ACL) | both **CLEAR** (no positive case in TerraGoat) |

## Claim
**"Checkov validates; the copilot differentiates."** Agreement is measured ONLY
on my implemented subset that TerraGoat positively exercises (**K→K**) — not
recall vs all 200+ Checkov checks. Completeness + labelled divergences are in
`LIMITATIONS.md`.
