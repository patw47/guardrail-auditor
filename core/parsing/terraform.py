"""Terraform (HCL) parser → normalized resources.

Structure comes from `python-hcl2` (v8: blocks are already lists tagged
`__is_block__`, scalars are quote-wrapped). Line numbers come from a
comment-stripped header scan — robust to comments/blank lines before a
resource, which is exactly where naive line tracking silently breaks.
"""

from __future__ import annotations

import re
from typing import Any

import hcl2

from models import Resource

from .errors import ParseError

_BLOCK_MARKER = "__is_block__"
_HEADER_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')


def _strip_comments(text: str) -> str:
    """Blank out comments while preserving line count (for the header scan)."""

    def _blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"/\*.*?\*/", _blank, text, flags=re.S)  # block comments
    out: list[str] = []
    for line in text.split("\n"):
        line = re.sub(r"#.*$", "", line)
        line = re.sub(r"//.*$", "", line)
        out.append(line)
    return "\n".join(out)


def _header_lines(text: str) -> dict[tuple[str, str], list[int]]:
    """Map (type, name) → the 1-based line(s) of its `resource` header."""
    out: dict[tuple[str, str], list[int]] = {}
    for lineno, line in enumerate(_strip_comments(text).split("\n"), start=1):
        match = _HEADER_RE.search(line)
        if match:
            out.setdefault((match.group(1), match.group(2)), []).append(lineno)
    return out


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def _clean(value: Any) -> Any:
    """Drop hcl2's `__is_block__` markers and unquote scalar strings."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items() if k != _BLOCK_MARKER}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, str):
        return _unquote(value)
    return value


def parse(content: str, filename: str) -> list[Resource]:
    """Parse Terraform HCL content into normalized resources."""
    try:
        data = hcl2.loads(content)
    except Exception as exc:  # lark/hcl2 raise a variety of parse errors
        raise ParseError(
            f"{filename}: invalid Terraform HCL ({exc.__class__.__name__})"
        ) from exc

    headers = _header_lines(content)
    consumed: dict[tuple[str, str], int] = {}
    resources: list[Resource] = []

    for block in data.get("resource", []):
        if not isinstance(block, dict):
            continue
        for type_label, name_map in block.items():
            rtype = _unquote(type_label)
            if not isinstance(name_map, dict):
                continue
            for name_label, attrs in name_map.items():
                rname = _unquote(name_label)
                key = (rtype, rname)
                lines = headers.get(key, [])
                idx = consumed.get(key, 0)
                line = lines[idx] if idx < len(lines) else (lines[-1] if lines else 1)
                consumed[key] = idx + 1
                cleaned = _clean(attrs) if isinstance(attrs, dict) else {}
                resources.append(
                    Resource(
                        format="terraform",
                        type=rtype,
                        name=rname,
                        attributes=cleaned,
                        file=filename,
                        line=line,
                    )
                )
    return resources
