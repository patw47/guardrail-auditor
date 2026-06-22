"""SQLAlchemy ORM tables — the persisted schema (S5 sensitive gate, approved).

Kept separate from the pure models/ dataclasses; the repository maps between
them. Cascades: Scan 1-1 Score, Scan 1-* Finding, Finding 1-* Control.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class ScanRow(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column()
    source_type: Mapped[str] = mapped_column()
    file_count: Mapped[int] = mapped_column()
    # repo_url for repo scans; NULL for uploads
    source_ref: Mapped[str | None] = mapped_column(nullable=True, default=None)

    score: Mapped[ScoreRow] = relationship(
        back_populates="scan", uselist=False, cascade="all, delete-orphan"
    )
    findings: Mapped[list[FindingRow]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )


class ScoreRow(Base):
    __tablename__ = "scores"

    scan_id: Mapped[str] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"), primary_key=True
    )
    value: Mapped[int] = mapped_column()
    grade: Mapped[str] = mapped_column()
    critical_count: Mapped[int] = mapped_column()
    high_count: Mapped[int] = mapped_column()
    medium_count: Mapped[int] = mapped_column()
    low_count: Mapped[int] = mapped_column()

    scan: Mapped[ScanRow] = relationship(back_populates="score")


class FindingRow(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"))
    rule_id: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    severity: Mapped[str] = mapped_column()
    resource_type: Mapped[str] = mapped_column()
    resource_name: Mapped[str] = mapped_column()
    file: Mapped[str] = mapped_column()
    line: Mapped[int] = mapped_column()
    evidence: Mapped[str] = mapped_column()
    explanation: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column()

    scan: Mapped[ScanRow] = relationship(back_populates="findings")
    controls: Mapped[list[ControlRow]] = relationship(
        back_populates="finding", cascade="all, delete-orphan"
    )


class ControlRow(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("findings.id", ondelete="CASCADE"))
    framework: Mapped[str] = mapped_column()
    control_id: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    reference_url: Mapped[str] = mapped_column()
    level: Mapped[str] = mapped_column()

    finding: Mapped[FindingRow] = relationship(back_populates="controls")
