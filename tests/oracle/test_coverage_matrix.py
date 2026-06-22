"""S7 Part A guard: the coverage matrix is real, complete, and not drifted.

Verdicts themselves are proven by the detector tests passing in this same CI run;
here we assert the manifest covers every detector (TP + near-miss, incl. the hard
conditioned-policy), names only real tests, labels every discrimination test, and
matches the committed matrix.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from rules.detectors import RULES

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST = ROOT / "tests" / "oracle" / "manifest.yaml"
MATRIX = ROOT / "docs" / "coverage_matrix.md"
DETECTOR_SRC = (ROOT / "tests" / "test_detectors.py").read_text()


def _cases() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST.read_text())["cases"]


def _fn(proving_test: str) -> str:
    return proving_test.split("::")[-1]


def _suite_discrimination_tests() -> set[str]:
    return {
        name
        for name in re.findall(r"def (test_\w+)\(", DETECTOR_SRC)
        if name.endswith(("_fires", "_silent"))
    }


def test_every_proving_test_exists() -> None:
    for case in _cases():
        fn = _fn(case["proving_test"])
        assert f"def {fn}(" in DETECTOR_SRC, f"manifest names a missing test: {fn}"


def test_every_detector_has_tp_and_near_miss() -> None:
    cases = _cases()
    for rule_id in RULES:
        kinds = {c["kind"] for c in cases if c["rule_id"] == rule_id}
        assert "true_positive" in kinds, f"{rule_id} has no true-positive case"
        assert "near_miss" in kinds, f"{rule_id} has no near-miss case"


def test_hard_conditioned_policy_near_miss_is_labelled() -> None:
    assert any(
        c["rule_id"] == "S3_PUBLIC_BUCKET"
        and c["kind"] == "near_miss"
        and "policy_conditioned" in c["fixture"]
        for c in _cases()
    ), "the hard wildcard+Condition near-miss must be in the manifest"


def test_no_discrimination_test_is_unlabelled() -> None:
    labelled = {_fn(c["proving_test"]) for c in _cases()}
    orphans = _suite_discrimination_tests() - labelled
    assert not orphans, f"discrimination tests missing from the manifest: {sorted(orphans)}"


def test_committed_matrix_matches_manifest() -> None:
    assert MATRIX.exists(), "run tools/coverage_matrix.py to generate docs/coverage_matrix.md"
    text = MATRIX.read_text()
    cases = _cases()
    for case in cases:
        assert _fn(case["proving_test"]) in text, "matrix is missing a manifest case — regenerate"
    rows = [
        line
        for line in text.splitlines()
        if line.startswith("| ") and "rule_id" not in line and "---" not in line
    ]
    assert len(rows) == len(cases), "matrix row count drifted from the manifest — regenerate"
