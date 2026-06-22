"""Scan pipeline — assemble the pure stages into one deterministic run."""

from __future__ import annotations

from dataclasses import dataclass

from core.compliance import map_finding, render
from core.config_source import ConfigSource
from core.parsing import parse_content
from core.scoring import WEIGHTS, score_findings
from models import Control, Finding, Resource
from rules import run_detectors

_SUPPORTED = (".tf", ".yaml", ".yml", ".json", ".template")


@dataclass
class MappedFinding:
    finding: Finding
    controls: list[Control]
    explanation: str
    weight: int


@dataclass
class ScoreSummary:
    value: int
    grade: str
    counts: dict[str, int]


@dataclass
class ScanResult:
    source_type: str
    file_count: int
    score: ScoreSummary
    items: list[MappedFinding]


def run_scan(source: ConfigSource) -> ScanResult:
    """Parse → detect → score → map → render, assembled deterministically."""
    files = list(source.iter_files())
    resources: list[Resource] = []
    for name, content in files:
        if name.lower().endswith(_SUPPORTED):
            resources.extend(parse_content(content, name))

    findings = run_detectors(resources)
    score = score_findings(findings)
    items = [
        MappedFinding(
            finding=f,
            controls=map_finding(f),
            explanation=render(f),
            weight=WEIGHTS[f.severity],
        )
        for f in findings
    ]
    summary = ScoreSummary(
        value=score.value,
        grade=score.grade,
        counts={str(k): v for k, v in score.counts.items()},
    )
    return ScanResult(
        source_type=source.source_type,
        file_count=len(files),
        score=summary,
        items=items,
    )
