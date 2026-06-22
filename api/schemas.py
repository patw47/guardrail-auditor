"""Pydantic response models — these drive the OpenAPI schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ControlOut(BaseModel):
    framework: str
    control_id: str
    title: str
    reference_url: str
    level: str
    label: str  # computed display cite (single source of truth, incl. section marker)


class FindingOut(BaseModel):
    rule_id: str
    title: str
    severity: str
    resource_type: str
    resource_name: str
    file: str
    line: int
    evidence: str
    explanation: str
    weight: int
    controls: list[ControlOut]


class ScoreOut(BaseModel):
    value: int
    grade: str
    counts: dict[str, int]


class ScanSummary(BaseModel):
    id: str
    created_at: datetime
    source_type: str
    file_count: int
    score: ScoreOut


class ScanDetail(ScanSummary):
    findings: list[FindingOut]


class RepoScanRequest(BaseModel):
    repo_url: str
