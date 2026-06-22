"""S2 (L3): discrimination pairs — each detector fires on its violation and
stays silent on a safe look-alike. The pairs are the deliverable.
"""

from __future__ import annotations

import random
from pathlib import Path

from core.parsing import parse_file
from models import Finding
from rules import run_detectors

FIX = Path(__file__).parent / "fixtures" / "detectors"


def _scan(fixture: str) -> list[Finding]:
    return run_detectors(parse_file(FIX / fixture))


def _ids(findings: list[Finding]) -> set[str]:
    return {f.rule_id for f in findings}


def _only(findings: list[Finding], rule_id: str) -> list[Finding]:
    return [f for f in findings if f.rule_id == rule_id]


# --- S3_PUBLIC_BUCKET ------------------------------------------------------

def test_s3_public_acl_fires() -> None:
    hits = _only(_scan("s3_public_acl.tf"), "S3_PUBLIC_BUCKET")
    assert len(hits) == 1
    assert hits[0].severity == "high"
    assert hits[0].resource_name == "public_acl"
    assert hits[0].line == 1


def test_s3_public_policy_fires() -> None:  # ADAPTER §2 true-positive (public via policy)
    assert "S3_PUBLIC_BUCKET" in _ids(_scan("s3_public_policy.tf"))


def test_s3_private_versioning_silent() -> None:  # ADAPTER §2 near-miss
    assert "S3_PUBLIC_BUCKET" not in _ids(_scan("s3_private_versioning.tf"))


def test_s3_conditioned_policy_silent() -> None:  # the hard Checkov false positive
    assert "S3_PUBLIC_BUCKET" not in _ids(_scan("s3_policy_conditioned.tf"))


def test_s3_public_cloudformation_fires() -> None:  # cross-format TP
    assert "S3_PUBLIC_BUCKET" in _ids(_scan("s3_public.yaml"))


# --- OPEN_SSH --------------------------------------------------------------

def test_open_ssh_fires() -> None:
    hits = _only(_scan("open_ssh_open.tf"), "OPEN_SSH")
    assert len(hits) == 1
    assert hits[0].severity == "critical"
    assert hits[0].resource_name == "open"


def test_open_ssh_restricted_silent() -> None:
    assert "OPEN_SSH" not in _ids(_scan("open_ssh_restricted.tf"))


def test_open_ssh_cloudformation_fires() -> None:  # cross-format TP
    assert "OPEN_SSH" in _ids(_scan("open_ssh.yaml"))


# --- UNENCRYPTED_STORAGE ---------------------------------------------------

def test_unencrypted_storage_fires() -> None:
    hits = _only(_scan("unencrypted_volume.tf"), "UNENCRYPTED_STORAGE")
    assert len(hits) == 1
    assert hits[0].severity == "high"


def test_encrypted_storage_silent() -> None:
    assert "UNENCRYPTED_STORAGE" not in _ids(_scan("encrypted_volume.tf"))


# --- PUBLIC_DB -------------------------------------------------------------

def test_public_db_fires() -> None:
    hits = _only(_scan("public_db.tf"), "PUBLIC_DB")
    assert len(hits) == 1
    # HIGH per current Trivy rds/disable_public_access.rego (not critical)
    assert hits[0].severity == "high"


def test_private_db_silent() -> None:
    assert "PUBLIC_DB" not in _ids(_scan("private_db.tf"))


# --- engine ----------------------------------------------------------------

def test_multi_violation_reports_all_four() -> None:
    findings = _scan("multi_violation.tf")
    assert _ids(findings) == {
        "S3_PUBLIC_BUCKET",
        "OPEN_SSH",
        "UNENCRYPTED_STORAGE",
        "PUBLIC_DB",
    }
    for f in findings:
        assert f.severity in {"critical", "high", "medium", "low"}
        assert f.line > 0
        assert f.file == "multi_violation.tf"


def test_engine_deterministic_under_shuffle() -> None:
    resources = parse_file(FIX / "multi_violation.tf")
    shuffled = list(resources)
    random.Random(0).shuffle(shuffled)
    assert run_detectors(resources) == run_detectors(shuffled)
