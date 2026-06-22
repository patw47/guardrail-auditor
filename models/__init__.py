"""models — domain types. Fills at S1 (resource), S2 (finding), S3 (score), S4 (control)."""

from .finding import Finding, Severity
from .resource import Format, Resource

__all__ = ["Finding", "Format", "Resource", "Severity"]
