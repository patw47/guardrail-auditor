"""Scan pipeline — assemble the pure stages into one deterministic run."""

from __future__ import annotations

from dataclasses import dataclass

from core.compliance import map_finding, render
from core.config_source import ConfigSource
from core.parsing import ParseError, parse_content
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


def run_scan(source: ConfigSource, strict: bool = True) -> ScanResult:
    """Parse → detect → score → map → render, assembled deterministically.

    `strict=True` (uploads): a malformed recognised file raises (→ 400).
    `strict=False` (repo scans): skip files that fail to parse, since a real repo
    may contain non-standalone template fragments.
    """
    files = list(source.iter_files())
    resources: list[Resource] = []
    for name, content in files:
        if not name.lower().endswith(_SUPPORTED):
            continue
        try:
            resources.extend(parse_content(content, name))
        except ParseError:
            if strict:
                raise

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
