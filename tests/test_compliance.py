"""S4: compliance mapping + deterministic render. Fence, governing rule, purity."""

from __future__ import annotations

from core.compliance import AVD_ANCHOR, CONTROL_MAP, map_finding, render
from models import Control, Finding
from rules.detectors import RULES

_NAMED_FRAMEWORKS = {"CIS", "SOC2", "ISO27001", "GDPR"}


def _f(rule_id: str, line: int = 1) -> Finding:
    title, severity = RULES[rule_id]
    return Finding(
        rule_id=rule_id,
        title=title,
        severity=severity,
        resource_type="aws_x",
        resource_name="r",
        file="main.tf",
        line=line,
        evidence="ev",
    )


def test_every_rule_maps_at_least_one_named_control() -> None:
    for rule_id in RULES:
        controls = map_finding(_f(rule_id))
        assert controls, f"{rule_id} maps to no control"
        for c in controls:
            assert c.framework in _NAMED_FRAMEWORKS
            assert c.reference_url.startswith("https://")


def test_governing_rule_avd_severity_equals_detector_severity() -> None:
    for rule_id, (_title, severity) in RULES.items():
        assert rule_id in AVD_ANCHOR, f"{rule_id} has no AVD anchor"
        assert AVD_ANCHOR[rule_id][1] == severity


def test_fence_no_control_id_outside_the_table() -> None:  # ADAPTER §1
    allowed = {(c.framework, c.control_id) for controls in CONTROL_MAP.values() for c in controls}
    for rule_id in RULES:
        for c in map_finding(_f(rule_id)):
            assert (c.framework, c.control_id) in allowed
    # an unknown rule_id yields nothing (no stray control_id invented)
    unknown = Finding("UNKNOWN", "t", "high", "x", "n", "f", 1, "e")
    assert map_finding(unknown) == []


def test_map_finding_does_not_mutate_the_table() -> None:
    before = len(CONTROL_MAP["OPEN_SSH"])
    got = map_finding(_f("OPEN_SSH"))
    got.append(Control("CIS", "9.9", "x", "https://example.com"))
    assert len(CONTROL_MAP["OPEN_SSH"]) == before  # table untouched


def test_render_is_deterministic() -> None:
    f = _f("OPEN_SSH")
    assert render(f) == render(f)


def test_render_no_line_has_no_none() -> None:
    text = render(_f("OPEN_SSH", line=0))
    assert "None" not in text
    assert "main.tf:0" not in text
    assert "at main.tf:" in text  # location degrades to file only, no line


def test_section_marker_is_visible_only_for_section_cites() -> None:
    # PUBLIC_DB carries a CIS section-level cite → must show "(section)"
    assert "(section)" in render(_f("PUBLIC_DB"))
    assert "§2.3 (section)" in render(_f("PUBLIC_DB"))
    # OPEN_SSH is all precise → no section marker
    assert "(section)" not in render(_f("OPEN_SSH"))


def test_render_lists_controls_and_primary_reference() -> None:
    text = render(_f("OPEN_SSH"))
    assert "CIS AWS v3.0.0 §5.2" in text
    assert "SOC 2 CC6.1" in text
    assert "ISO 27001:2022 A.8.20" in text
    assert "Reference: https://www.cisecurity.org/benchmark/amazon_web_services." in text
