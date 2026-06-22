"""S8: guard against a lying README — it must name the REAL commands, fixtures,
and endpoints, and reference files that actually exist."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text()


def test_readme_names_real_commands() -> None:
    for token in ['pip install -e ".[dev]"', "uvicorn main:app", "pytest", "tools/demo_seed.py"]:
        assert token in README, f"README is missing the real command: {token}"


def test_readme_names_real_endpoints() -> None:
    for token in ["/api/scans", "/api/scans/repo", "/api/scans/{id}/rescan", "/openapi.json"]:
        assert token in README, f"README is missing endpoint: {token}"


def test_readme_references_existing_inputs() -> None:
    assert "tests/fixtures/detectors" in README
    assert (ROOT / "tests" / "fixtures" / "detectors" / "multi_violation.tf").exists()
    assert "bridgecrewio/terragoat" in README
    assert "docs/coverage_matrix.md" in README
    assert (ROOT / "docs" / "coverage_matrix.md").exists()
