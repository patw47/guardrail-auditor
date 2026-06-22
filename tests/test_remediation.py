"""S8: remediation is per-rule, consistent with the cited control, and fenced."""

from __future__ import annotations

from core.compliance import CONTROL_MAP
from core.remediation import REMEDIATIONS, remediate
from rules.detectors import RULES


def test_every_rule_has_a_remediation() -> None:
    for rule_id in RULES:
        rem = remediate(rule_id)
        assert rem is not None, f"{rule_id} has no remediation"
        assert rem.summary and rem.snippet


def test_remediation_keyset_matches_the_mapping() -> None:
    # consistent with the cited control: same rule_ids as the compliance mapping
    assert set(REMEDIATIONS) == set(CONTROL_MAP)


def test_remediation_summary_references_the_cited_control() -> None:
    # the fix names the control the finding cites (not a generic suggestion)
    expected = {
        "OPEN_SSH": "5.2",
        "S3_PUBLIC_BUCKET": "2.1.4",
        "UNENCRYPTED_STORAGE": "2.2.1",
        "PUBLIC_DB": "A.8.20",
    }
    for rule_id, token in expected.items():
        assert token in remediate(rule_id).summary  # type: ignore[union-attr]


def test_fence_unknown_rule_has_no_remediation() -> None:
    assert remediate("NOT_A_RULE") is None
