"""The Score model — the aggregated 0–100 Risk Score with its per-finding breakdown."""

from __future__ import annotations

from dataclasses import dataclass

from models.finding import Severity


@dataclass
class ScoreItem:
    """One finding's contribution to the Risk Score."""

    rule_id: str
    severity: Severity
    resource_type: str
    resource_name: str
    file: str
    line: int
    weight: int


@dataclass
class Score:
    """The aggregated posture: a 0–100 risk value, a letter grade, severity
    counts, and the per-finding breakdown (so the number is explainable)."""

    value: int
    grade: str
    counts: dict[Severity, int]
    breakdown: list[ScoreItem]
