"""Persistence: map ScanResult <-> ORM rows. Save and load by id."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.pipeline import MappedFinding, ScanResult, ScoreSummary
from core.tables import ControlRow, FindingRow, ScanRow, ScoreRow
from models import Control, Finding
from models.control import Framework, Level
from models.finding import Severity


def save_scan(session: Session, result: ScanResult, source_ref: str | None = None) -> str:
    scan_id = str(uuid.uuid4())
    scan = ScanRow(
        id=scan_id,
        created_at=datetime.now(UTC),
        source_type=result.source_type,
        file_count=result.file_count,
        source_ref=source_ref,
    )
    scan.score = ScoreRow(
        value=result.score.value,
        grade=result.score.grade,
        critical_count=result.score.counts.get("critical", 0),
        high_count=result.score.counts.get("high", 0),
        medium_count=result.score.counts.get("medium", 0),
        low_count=result.score.counts.get("low", 0),
    )
    for item in result.items:
        f = item.finding
        row = FindingRow(
            rule_id=f.rule_id,
            title=f.title,
            severity=f.severity,
            resource_type=f.resource_type,
            resource_name=f.resource_name,
            file=f.file,
            line=f.line,
            evidence=f.evidence,
            explanation=item.explanation,
            weight=item.weight,
        )
        for c in item.controls:
            row.controls.append(
                ControlRow(
                    framework=c.framework,
                    control_id=c.control_id,
                    title=c.title,
                    reference_url=c.reference_url,
                    level=c.level,
                )
            )
        scan.findings.append(row)

    session.add(scan)
    session.commit()
    return scan_id


def get_scan(session: Session, scan_id: str) -> ScanRow | None:
    return session.get(ScanRow, scan_id)


def list_scans(session: Session) -> Sequence[ScanRow]:
    return session.scalars(select(ScanRow).order_by(ScanRow.created_at.desc())).all()


def load_result(session: Session, scan_id: str) -> ScanResult | None:
    """Reconstruct the pipeline-shaped ScanResult from persisted rows (for the
    persisted-vs-pipeline round-trip check)."""
    row = session.get(ScanRow, scan_id)
    if row is None:
        return None

    items: list[MappedFinding] = []
    for fr in sorted(row.findings, key=lambda r: (r.file, r.line, r.rule_id)):
        finding = Finding(
            rule_id=fr.rule_id,
            title=fr.title,
            severity=cast(Severity, fr.severity),
            resource_type=fr.resource_type,
            resource_name=fr.resource_name,
            file=fr.file,
            line=fr.line,
            evidence=fr.evidence,
        )
        controls = [
            Control(
                framework=cast(Framework, c.framework),
                control_id=c.control_id,
                title=c.title,
                reference_url=c.reference_url,
                level=cast(Level, c.level),
            )
            for c in sorted(fr.controls, key=lambda c: c.id)
        ]
        items.append(
            MappedFinding(
                finding=finding,
                controls=controls,
                explanation=fr.explanation,
                weight=fr.weight,
            )
        )

    summary = ScoreSummary(
        value=row.score.value,
        grade=row.score.grade,
        counts={
            "critical": row.score.critical_count,
            "high": row.score.high_count,
            "medium": row.score.medium_count,
            "low": row.score.low_count,
        },
    )
    return ScanResult(
        source_type=row.source_type,
        file_count=row.file_count,
        score=summary,
        items=items,
    )
