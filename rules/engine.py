"""The detector engine: run detectors over resources → deterministically ordered findings."""

from __future__ import annotations

from collections.abc import Sequence

from models import Finding, Resource

from .detectors import DETECTORS, Detector


def run_detectors(
    resources: Sequence[Resource],
    detectors: Sequence[Detector] | None = None,
) -> list[Finding]:
    """Run every detector against every resource.

    Output is sorted by (file, line, rule_id) so the result is independent of
    resource/detector input order — same input, same findings, every run.
    """
    active = list(DETECTORS if detectors is None else detectors)
    findings: list[Finding] = []
    for resource in resources:
        for detector in active:
            finding = detector(resource)
            if finding is not None:
                findings.append(finding)
    findings.sort(key=lambda f: (f.file, f.line, f.rule_id))
    return findings
