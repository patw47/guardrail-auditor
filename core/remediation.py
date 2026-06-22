"""Per-rule remediation — the fix that closes the SAME rule the finding cites.

Keyed by rule_id (the join key shared with core.compliance.CONTROL_MAP); each
summary references the same control the finding maps to. Pure + fenced.
"""

from __future__ import annotations

from models.remediation import Remediation

REMEDIATIONS: dict[str, Remediation] = {
    "OPEN_SSH": Remediation(
        summary="Restrict SSH ingress to a trusted CIDR instead of 0.0.0.0/0 "
        "(closes CIS AWS v3.0.0 §5.2).",
        snippet=(
            'ingress {\n'
            '  from_port   = 22\n'
            '  to_port     = 22\n'
            '  protocol    = "tcp"\n'
            '  cidr_blocks = ["10.0.0.0/8"]  # a trusted range, not 0.0.0.0/0\n'
            '}'
        ),
    ),
    "S3_PUBLIC_BUCKET": Remediation(
        summary="Set acl=private and enable S3 Block Public Access "
        "(closes CIS AWS v3.0.0 §2.1.4).",
        snippet=(
            'resource "aws_s3_bucket_public_access_block" "this" {\n'
            '  bucket                  = aws_s3_bucket.example.id\n'
            '  block_public_acls       = true\n'
            '  block_public_policy     = true\n'
            '  ignore_public_acls      = true\n'
            '  restrict_public_buckets = true\n'
            '}'
        ),
        cli=(
            "aws s3api put-public-access-block --bucket <name> "
            "--public-access-block-configuration "
            "BlockPublicAcls=true,BlockPublicPolicy=true,"
            "IgnorePublicAcls=true,RestrictPublicBuckets=true"
        ),
    ),
    "UNENCRYPTED_STORAGE": Remediation(
        summary="Enable encryption at rest (closes CIS AWS v3.0.0 §2.2.1).",
        snippet="encrypted         = true  # EBS\n# storage_encrypted = true  # RDS",
    ),
    "PUBLIC_DB": Remediation(
        summary="Set publicly_accessible=false so the database is not "
        "internet-reachable (closes ISO 27001:2022 A.8.20).",
        snippet="publicly_accessible = false",
    ),
}


def remediate(rule_id: str) -> Remediation | None:
    """The remediation for a rule, or None if the rule has none (fence)."""
    return REMEDIATIONS.get(rule_id)
