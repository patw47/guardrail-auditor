"""The Remediation model — the corrected IaC snippet / CLI action for a rule.

Keyed by the same rule_id as the compliance mapping, so the fix closes the very
rule the finding cites (not a generic suggestion). Deterministic, no LLM.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Remediation:
    summary: str
    snippet: str
    cli: str | None = None
