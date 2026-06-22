"""Parsing errors."""

from __future__ import annotations


class ParseError(ValueError):
    """Raised when an IaC file cannot be parsed into normalized resources.

    Carries a short, file-scoped message — never a raw library stacktrace.
    """
