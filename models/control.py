"""The Control model — a named compliance control a finding maps to.

`level` makes the precision visible: a `precise` cite is a verified control
number; a `section` cite is a benchmark section (used when a precise sub-number
could not be verified) — a reader must never mistake one for the other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Framework = Literal["CIS", "SOC2", "ISO27001", "GDPR"]
Level = Literal["precise", "section"]

_FRAMEWORK_LABEL: dict[Framework, str] = {
    "CIS": "CIS AWS v3.0.0",
    "SOC2": "SOC 2",
    "ISO27001": "ISO 27001:2022",
    "GDPR": "GDPR",
}


@dataclass(frozen=True)
class Control:
    framework: Framework
    control_id: str
    title: str
    reference_url: str
    level: Level = "precise"

    @property
    def label(self) -> str:
        """Human-readable cite, with the section marker made visible."""
        cid = f"§{self.control_id}" if self.framework == "CIS" else self.control_id
        marker = " (section)" if self.level == "section" else ""
        return f"{_FRAMEWORK_LABEL[self.framework]} {cid}{marker}"
