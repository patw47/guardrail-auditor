"""S3: the pure Risk Score — edge cases, weighting, grade bands + severity floor,
order-independent determinism, monotonicity.
"""

from __future__ import annotations

import random

from core.scoring import WEIGHTS, score_findings
from models import Finding, Severity


def _f(severity: Severity, rule_id: str = "R", line: int = 1) -> Finding:
    return Finding(
        rule_id=rule_id,
        title="t",
        severity=severity,
        resource_type="rt",
        resource_name="rn",
        file="f.tf",
        line=line,
        evidence="e",
    )


def _lows(n: int) -> list[Finding]:
    return [_f("low", rule_id=f"L{i}", line=i) for i in range(n)]


def test_empty_is_zero_grade_a() -> None:
    s = score_findings([])
    assert s.value == 0
    assert s.grade == "A"
    assert s.counts == {"critical": 0, "high": 0, "medium": 0, "low": 0}
    assert s.breakdown == []


def test_all_critical_caps_at_100_grade_f() -> None:
    s = score_findings([_f("critical", rule_id=f"C{i}") for i in range(3)])  # 150 → cap
    assert s.value == 100
    assert s.grade == "F"


def test_one_critical_outranks_two_highs() -> None:
    assert score_findings([_f("critical")]).value == 50
    assert score_findings([_f("high"), _f("high")]).value == 30
    assert score_findings([_f("critical")]).value > score_findings([_f("high"), _f("high")]).value


def test_grade_band_boundaries() -> None:
    # Built from low-severity findings so only the numeric band is exercised.
    assert score_findings(_lows(0)).grade == "A"
    assert score_findings(_lows(19)).grade == "B"
    assert score_findings(_lows(20)).grade == "C"
    assert score_findings(_lows(39)).grade == "C"
    assert score_findings(_lows(40)).grade == "D"
    assert score_findings(_lows(69)).grade == "D"
    assert score_findings(_lows(70)).grade == "F"


def test_severity_floor() -> None:
    # A lone high scores 15 (numeric band B) but floors to C.
    high = score_findings([_f("high")])
    assert high.value == 15
    assert high.grade == "C"
    # A lone critical scores 50 (band D) and floors to D.
    assert score_findings([_f("critical")]).grade == "D"
    # The floor only worsens — it never improves a worse numeric grade.
    assert score_findings([_f("critical") for _ in range(3)]).grade == "F"


def test_breakdown_is_per_finding_and_weighted() -> None:
    findings = [_f("critical"), _f("high"), _f("low")]
    s = score_findings(findings)
    assert len(s.breakdown) == len(findings)
    for item in s.breakdown:
        assert item.weight == WEIGHTS[item.severity]
    assert sum(item.weight for item in s.breakdown) == 50 + 15 + 1  # pre-cap raw


def test_determinism_under_shuffle() -> None:
    findings = [
        _f("critical", rule_id="OPEN_SSH"),
        _f("high", rule_id="S3_PUBLIC_BUCKET"),
        _f("high", rule_id="PUBLIC_DB"),
        _f("low", rule_id="X"),
    ]
    shuffled = list(findings)
    random.Random(0).shuffle(shuffled)
    assert score_findings(findings) == score_findings(shuffled)


def test_monotonic_adding_a_finding_never_lowers_value() -> None:
    base: list[Finding] = []
    for extra in [_f("low"), _f("high"), _f("critical"), _f("medium")]:
        before = score_findings(base).value
        base = [*base, extra]
        assert score_findings(base).value >= before
