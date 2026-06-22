"""The Finding model — one detected violation, before scoring (S3) and control mapping (S4)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["critical", "high", "medium", "low"]


@dataclass
class Finding:
    """A single rule violation against one resource.

    `rule_id` is the stable join key the S4 control mapping keys on; `severity`
    is the AVD/CIS-anchored weight the S3 score uses; `evidence` is the
    plain-language reason this fired.
    """

    rule_id: str
    title: str
    severity: Severity
    resource_type: str
    resource_name: str
    file: str
    line: int
    evidence: str
