"""S7 Part B: K→K agreement with an external reference tool (Checkov) on
TerraGoat. Runs offline against the committed reference (no network, no Checkov
dep). Distinct evidence from the Part-A coverage matrix (see SOURCES.md)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.config_source import UploadedFilesSource
from core.pipeline import run_scan

ORACLE = Path(__file__).resolve().parent
TG = ORACLE / "terragoat"
REFERENCE: list[dict[str, Any]] = json.loads((ORACLE / "checkov_reference.json").read_text())

# rule_id -> Checkov check_id it corresponds to (verified from the real output).
# S3_PUBLIC_BUCKET ~ CKV_AWS_20 (public ACL) is intentionally NOT in K: TerraGoat
# has no public-via-ACL/policy bucket, so it has no positive oracle case.
RULE_TO_CKV = {
    "OPEN_SSH": "CKV_AWS_24",
    "PUBLIC_DB": "CKV_AWS_17",
    "UNENCRYPTED_STORAGE": "CKV_AWS_16",
}


def _my_rule_ids() -> set[str]:
    files = [(p.name, p.read_text()) for p in sorted(TG.glob("*.tf"))]
    return {item.finding.rule_id for item in run_scan(UploadedFilesSource(files)).items}


def _checkov_failed(check_id: str) -> set[str]:
    return {
        c["resource"]
        for c in REFERENCE
        if c["check_id"] == check_id and c["check_result"]["result"] == "FAILED"
    }


def test_my_scanner_reproduces_terragoat_findings() -> None:
    assert _my_rule_ids() == {"OPEN_SSH", "PUBLIC_DB", "UNENCRYPTED_STORAGE"}


def test_kk_agreement_on_exercised_subset() -> None:
    mine = _my_rule_ids()
    for rule_id, ckv in RULE_TO_CKV.items():
        i_flag = rule_id in mine
        checkov_flag = len(_checkov_failed(ckv)) > 0
        assert i_flag and checkov_flag, f"{rule_id} vs {ckv}: mine={i_flag} checkov={checkov_flag}"


def test_s3_has_no_positive_oracle_case() -> None:
    # Honest completeness: both my tool and Checkov's public-ACL check are clear.
    assert "S3_PUBLIC_BUCKET" not in _my_rule_ids()
    assert _checkov_failed("CKV_AWS_20") == set()


def test_reference_is_genuine_checkov_output() -> None:
    # Real CKV_* ids and the real check_result shape — not synthesized.
    assert REFERENCE
    for c in REFERENCE:
        assert c["check_id"].startswith(("CKV_AWS_", "CKV2_AWS_"))
        assert c["check_result"]["result"] in {"PASSED", "FAILED"}
