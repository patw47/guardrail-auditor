"""REST API — scan endpoints. Uploaded-files source only (repo-URL = S5b)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import cast

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.schemas import ControlOut, FindingOut, RepoScanRequest, ScanDetail, ScanSummary, ScoreOut
from core.config_source import (
    ConfigSourceError,
    RepoUrlSource,
    UploadedFilesSource,
    validate_repo_url,
)
from core.db import SessionLocal
from core.parsing import ParseError
from core.pipeline import run_scan
from core.repository import get_scan, list_scans, save_scan
from core.tables import ControlRow, FindingRow, ScanRow
from models import Control
from models.control import Framework, Level

router = APIRouter()


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sorted_findings(row: ScanRow) -> list[FindingRow]:
    return sorted(row.findings, key=lambda r: (r.file, r.line, r.rule_id))


def _control_out(c: ControlRow) -> ControlOut:
    # Reuse the domain Control.label so the section marker can't drift in the UI.
    domain = Control(
        framework=cast(Framework, c.framework),
        control_id=c.control_id,
        title=c.title,
        reference_url=c.reference_url,
        level=cast(Level, c.level),
    )
    return ControlOut(
        framework=c.framework,
        control_id=c.control_id,
        title=c.title,
        reference_url=c.reference_url,
        level=c.level,
        label=domain.label,
    )


def _finding_out(fr: FindingRow) -> FindingOut:
    return FindingOut(
        rule_id=fr.rule_id,
        title=fr.title,
        severity=fr.severity,
        resource_type=fr.resource_type,
        resource_name=fr.resource_name,
        file=fr.file,
        line=fr.line,
        evidence=fr.evidence,
        explanation=fr.explanation,
        weight=fr.weight,
        controls=[_control_out(c) for c in sorted(fr.controls, key=lambda c: c.id)],
    )


def _score_out(row: ScanRow) -> ScoreOut:
    s = row.score
    return ScoreOut(
        value=s.value,
        grade=s.grade,
        counts={
            "critical": s.critical_count,
            "high": s.high_count,
            "medium": s.medium_count,
            "low": s.low_count,
        },
    )


def _summary(row: ScanRow) -> ScanSummary:
    return ScanSummary(
        id=row.id,
        created_at=row.created_at,
        source_type=row.source_type,
        file_count=row.file_count,
        score=_score_out(row),
    )


def _detail(row: ScanRow) -> ScanDetail:
    return ScanDetail(
        id=row.id,
        created_at=row.created_at,
        source_type=row.source_type,
        file_count=row.file_count,
        score=_score_out(row),
        findings=[_finding_out(fr) for fr in _sorted_findings(row)],
    )


@router.post("/scans", status_code=201, response_model=ScanDetail)
async def create_scan(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> ScanDetail:
    payload: list[tuple[str, str]] = []
    for upload in files:
        raw = await upload.read()
        payload.append((upload.filename or "unnamed", raw.decode("utf-8", errors="replace")))
    try:
        result = run_scan(UploadedFilesSource(payload))
    except ParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    scan_id = save_scan(db, result)
    row = get_scan(db, scan_id)
    if row is None:  # pragma: no cover - just saved
        raise HTTPException(status_code=500, detail="scan vanished after save")
    return _detail(row)


@router.get("/scans", response_model=list[ScanSummary])
def get_scans(db: Session = Depends(get_db)) -> list[ScanSummary]:
    return [_summary(r) for r in list_scans(db)]


@router.get("/scans/{scan_id}", response_model=ScanDetail)
def get_scan_detail(scan_id: str, db: Session = Depends(get_db)) -> ScanDetail:
    row = get_scan(db, scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="scan not found")
    return _detail(row)


@router.get("/scans/{scan_id}/findings", response_model=list[FindingOut])
def get_scan_findings(scan_id: str, db: Session = Depends(get_db)) -> list[FindingOut]:
    row = get_scan(db, scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="scan not found")
    return [_finding_out(fr) for fr in _sorted_findings(row)]


@router.get("/scans/{scan_id}/score", response_model=ScoreOut)
def get_scan_score(scan_id: str, db: Session = Depends(get_db)) -> ScoreOut:
    row = get_scan(db, scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="scan not found")
    return _score_out(row)


def _scan_repo(db: Session, repo_url: str) -> ScanDetail:
    """Validate (SSRF guard) → clone → scan → persist. Shared by repo-scan + rescan."""
    try:
        validate_repo_url(repo_url)
    except ConfigSourceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        result = run_scan(RepoUrlSource(repo_url), strict=False)
    except ConfigSourceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # clone/parse failure on a real repo
        raise HTTPException(
            status_code=502, detail=f"repo scan failed: {exc.__class__.__name__}"
        ) from exc
    scan_id = save_scan(db, result, source_ref=repo_url)
    row = get_scan(db, scan_id)
    if row is None:  # pragma: no cover - just saved
        raise HTTPException(status_code=500, detail="scan vanished after save")
    return _detail(row)


@router.post("/scans/repo", status_code=201, response_model=ScanDetail)
def create_repo_scan(body: RepoScanRequest, db: Session = Depends(get_db)) -> ScanDetail:
    return _scan_repo(db, body.repo_url)


@router.post("/scans/{scan_id}/rescan", status_code=201, response_model=ScanDetail)
def rescan(scan_id: str, db: Session = Depends(get_db)) -> ScanDetail:
    src = get_scan(db, scan_id)
    if src is None:
        raise HTTPException(status_code=404, detail="scan not found")
    if src.source_type != "repo_url" or not src.source_ref:
        raise HTTPException(status_code=409, detail="source not re-fetchable (upload)")
    return _scan_repo(db, src.source_ref)
