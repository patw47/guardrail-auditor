"""Risk Score — pure, deterministic, severity-weighted aggregation.

No I/O, no LLM, no persistence. Same findings → same Score, every run, regardless
of input order. Dials (weights / bands / severity-floor) are documented in
memory/decisions.md so the number is auditable.
"""

from __future__ import annotations

from collections.abc import Sequence

from models import Finding, Score, ScoreItem
from models.finding import Severity

# Severity weights — additive, then capped at 100. Tuned so ONE critical (50)
# outranks TWO highs (30): a single critical already reads as serious.
WEIGHTS: dict[Severity, int] = {"critical": 50, "high": 15, "medium": 5, "low": 1}

# Grade order, worst-last; index is the rank used for the severity floor.
_GRADES = ("A", "B", "C", "D", "F")

# Deterministic ordering of the breakdown and reproducible counts.
_SEVERITY_RANK: dict[Severity, int] = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _band_rank(value: int) -> int:
    """Numeric band: 0→A, 1–19→B, 20–39→C, 40–69→D, 70–100→F."""
    if value == 0:
        return 0
    if value <= 19:
        return 1
    if value <= 39:
        return 2
    if value <= 69:
        return 3
    return 4


def _floor_rank(findings: Sequence[Finding]) -> int:
    """Severity floor: any critical ⇒ grade ≤ D (3); else any high ⇒ ≤ C (2)."""
    severities = {f.severity for f in findings}
    if "critical" in severities:
        return 3
    if "high" in severities:
        return 2
    return 0


def score_findings(findings: Sequence[Finding]) -> Score:
    raw = sum(WEIGHTS[f.severity] for f in findings)
    value = min(100, raw)
    grade = _GRADES[max(_band_rank(value), _floor_rank(findings))]

    counts: dict[Severity, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        counts[finding.severity] += 1

    breakdown = sorted(
        (
            ScoreItem(
                rule_id=f.rule_id,
                severity=f.severity,
                resource_type=f.resource_type,
                resource_name=f.resource_name,
                file=f.file,
                line=f.line,
                weight=WEIGHTS[f.severity],
            )
            for f in findings
        ),
        key=lambda i: (_SEVERITY_RANK[i.severity], i.rule_id, i.file, i.line),
    )
    return Score(value=value, grade=grade, counts=counts, breakdown=breakdown)
