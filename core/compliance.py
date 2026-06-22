"""Compliance mapping + deterministic explanation. No LLM, no network at runtime.

`finding.rule_id → named compliance controls` via a static, verified table, plus
a pure `render()` template. The AVD entry is a SEPARATE severity-anchor (used by
the governing-rule check) — it is NOT a compliance framework and is never
rendered as a control.
"""

from __future__ import annotations

from models import Control, Finding
from models.finding import Severity

# AVD severity anchor — provenance for each rule's severity, NOT a compliance
# control. Shape: rule_id -> (avd ref, stated severity, url). Used only by the
# governing-rule test (AVD severity must equal the detector severity).
AVD_ANCHOR: dict[str, tuple[str, Severity, str]] = {
    "OPEN_SSH": ("AVD-AWS-0107", "critical", "https://avd.aquasec.com/misconfig/avd-aws-0107"),
    "S3_PUBLIC_BUCKET": (
        "aws-s3-no-public-access-with-acl",
        "high",
        "https://avd.aquasec.com/misconfig/aws/s3/no-public-access-with-acl/",
    ),
    "UNENCRYPTED_STORAGE": (
        "aws-ec2-enable-volume-encryption",
        "high",
        "https://avd.aquasec.com/misconfig/aws/ec2/enable-volume-encryption/",
    ),
    "PUBLIC_DB": ("AVD-AWS-0011", "high", "https://avd.aquasec.com/misconfig/avd-aws-0011"),
}

_CIS = "https://www.cisecurity.org/benchmark/amazon_web_services"
_SOC2 = (
    "https://www.aicpa-cima.com/resources/landing/"
    "system-and-organization-controls-soc-suite-of-services"
)
_ISO = "https://www.iso.org/standard/27001"
_GDPR32 = "https://gdpr-info.eu/art-32-gdpr/"

# rule_id -> named compliance controls, PRIMARY first (drives render's Reference).
CONTROL_MAP: dict[str, list[Control]] = {
    "OPEN_SSH": [
        Control("CIS", "5.2", "No SG ingress from 0.0.0.0/0 to remote admin ports", _CIS),
        Control("SOC2", "CC6.1", "Logical access controls", _SOC2),
        Control("ISO27001", "A.8.20", "Networks security", _ISO),
    ],
    "S3_PUBLIC_BUCKET": [
        Control("CIS", "2.1.4", "S3 Block Public Access enabled", _CIS),
        Control("SOC2", "CC6.1", "Logical access controls", _SOC2),
        Control("ISO27001", "A.5.15", "Access control", _ISO),
        Control("GDPR", "Art. 32", "Security of processing", _GDPR32),
    ],
    "UNENCRYPTED_STORAGE": [
        Control("CIS", "2.2.1", "EBS volume encryption enabled", _CIS),
        Control("ISO27001", "A.8.24", "Use of cryptography", _ISO),
        Control("GDPR", "Art. 32", "Security of processing", _GDPR32),
    ],
    "PUBLIC_DB": [
        Control("ISO27001", "A.8.20", "Networks security", _ISO),
        Control("CIS", "2.3", "RDS (precise sub-number unverified)", _CIS, level="section"),
    ],
}


def map_finding(finding: Finding) -> list[Control]:
    """Named compliance controls for a finding (a copy — the table is immutable
    to callers). Unknown rule_id → empty list (ADAPTER §1 fence)."""
    return list(CONTROL_MAP.get(finding.rule_id, []))


def _location(finding: Finding) -> str:
    return f"{finding.file}:{finding.line}" if finding.line else finding.file


def render(finding: Finding) -> str:
    """Deterministic, pure explanation. Same finding → same text. No LLM."""
    controls = map_finding(finding)
    compliance = "; ".join(c.label for c in controls) if controls else "none mapped"
    text = (
        f"{finding.severity.upper()} — {finding.title}. "
        f"{finding.resource_type} '{finding.resource_name}' at {_location(finding)}: "
        f"{finding.evidence}. Compliance: {compliance}."
    )
    if controls:
        text += f" Reference: {controls[0].reference_url}."
    return text
