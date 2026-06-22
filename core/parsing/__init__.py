"""core.parsing — the ingest layer: IaC files → normalized resources.

Public API: `parse_file`, `parse_content`, `ParseError`. Format is chosen by
file extension (`.tf` → Terraform; `.yaml`/`.yml`/`.json`/`.template` → CFN).
`.tf.json` (Terraform JSON syntax) is out of scope for S1 (TF-first = HCL).
"""

from __future__ import annotations

from pathlib import Path

from models import Resource

from . import cloudformation, terraform
from .errors import ParseError

__all__ = ["ParseError", "parse_content", "parse_file"]

_CFN_SUFFIXES = (".yaml", ".yml", ".json", ".template")


def parse_content(content: str, filename: str) -> list[Resource]:
    name = filename.lower()
    if name.endswith(".tf"):
        return terraform.parse(content, filename)
    if name.endswith(_CFN_SUFFIXES):
        return cloudformation.parse(content, filename)
    raise ParseError(
        f"{filename}: unsupported file type "
        "(expected .tf or CloudFormation .yaml/.yml/.json/.template)"
    )


def parse_file(path: str | Path) -> list[Resource]:
    p = Path(path)
    try:
        content = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ParseError(f"{p.name}: file is not valid UTF-8") from exc
    return parse_content(content, p.name)
