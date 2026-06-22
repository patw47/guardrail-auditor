"""models — domain types. Fills at S1 (resource), S2 (finding), S3 (score), S4 (control)."""

from .control import Control, Framework
from .finding import Finding, Severity
from .resource import Format, Resource
from .score import Score, ScoreItem

__all__ = [
    "Control",
    "Finding",
    "Format",
    "Framework",
    "Resource",
    "Score",
    "ScoreItem",
    "Severity",
]
