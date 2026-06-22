"""S6 (dep-light behavioral): the dashboard is served, consumes /api only, and
the served stack carries every field the UI renders. DOM render is checked by a
manual screenshot (see decisions.md), not here."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from main import app

FIX = Path(__file__).parent / "fixtures"
WEB = Path(__file__).parent.parent / "web"


def _post(client: TestClient, fixture: Path) -> dict:
    return client.post(
        "/api/scans",
        files=[("files", (fixture.name, fixture.read_text(), "text/plain"))],
    ).json()


def test_index_served_with_shell() -> None:
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        for token in [
            'id="files"', 'id="scan"', 'id="repo-url"', 'id="scan-repo"', 'id="rescan"',
            "Risk Score", "Severity", "Compliance",
            'id="gauge-arc"', 'id="empty"', "/static/app.js",
        ]:
            assert token in r.text


def test_static_assets_served() -> None:
    with TestClient(app) as client:
        assert client.get("/static/app.js").status_code == 200
        assert client.get("/static/styles.css").status_code == 200


def test_app_js_wires_api_and_fields() -> None:
    js = (WEB / "static" / "app.js").read_text()
    for token in [
        "/api/scans", "/api/scans/repo", "/rescan", "source_type",
        "FormData", "res.ok", "severity.toUpperCase()",
        "c.label", "reference_url", "findings.length", "showError",
    ]:
        assert token in js, f"app.js missing wiring: {token}"


def test_severity_conveyed_by_colour_and_text() -> None:
    css = (WEB / "static" / "styles.css").read_text()
    for cls in [".sev-critical", ".sev-high", ".sev-medium", ".sev-low"]:
        assert cls in css  # colour
    js = (WEB / "static" / "app.js").read_text()
    assert "toUpperCase()" in js  # text label, not colour alone


def test_served_stack_carries_every_rendered_field() -> None:
    with TestClient(app) as client:
        data = _post(client, FIX / "detectors" / "multi_violation.tf")
        assert {"value", "grade", "counts"} <= data["score"].keys()
        assert data["score"]["value"] == 95
        assert data["score"]["grade"] == "F"
        assert data["findings"]
        for f in data["findings"]:
            assert {
                "severity", "title", "resource_type", "resource_name",
                "file", "line", "explanation", "controls",
            } <= f.keys()
            assert f["controls"]
            for c in f["controls"]:
                assert {"framework", "control_id", "level", "reference_url", "label"} <= c.keys()
                assert c["reference_url"].startswith("https://")
        # the section marker survives all the way to the rendered label
        labels = [c["label"] for f in data["findings"] for c in f["controls"]]
        assert any("(section)" in label for label in labels)


def test_empty_state_clean_fixture_scores_zero() -> None:
    with TestClient(app) as client:
        data = _post(client, FIX / "clean" / "clean.tf")
        assert data["score"]["value"] == 0
        assert data["score"]["grade"] == "A"
        assert data["findings"] == []
    js = (WEB / "static" / "app.js").read_text()
    assert '"empty"' in js  # the JS has an empty-state branch


def test_error_state_malformed_returns_400() -> None:
    bad = (FIX / "terraform" / "malformed.tf").read_text()
    with TestClient(app) as client:
        r = client.post("/api/scans", files=[("files", ("malformed.tf", bad, "text/plain"))])
        assert r.status_code == 400
    js = (WEB / "static" / "app.js").read_text()
    assert "showError" in js  # the JS surfaces the error state
