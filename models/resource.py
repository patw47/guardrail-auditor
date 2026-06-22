"""The normalized resource model — the single shape both parsers converge on."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Format = Literal["terraform", "cloudformation"]


@dataclass
class Resource:
    """A single IaC resource, normalized across Terraform and CloudFormation.

    `type` is the native type string (`aws_s3_bucket` / `AWS::S3::Bucket`);
    `name` is the TF resource label or the CFN logical id; `attributes` is the
    resource body with format quirks absorbed (nested blocks are always lists,
    HCL scalars unquoted); `file`/`line` point at the resource header.
    """

    format: Format
    type: str
    name: str
    attributes: dict[str, Any]
    file: str
    line: int
