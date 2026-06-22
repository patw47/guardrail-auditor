"""The deterministic detectors. Each maps BOTH Terraform and CloudFormation
native shapes onto one rule and returns a Finding or None.

Severities are anchored to a citable authority (AVD / CIS) so the S3 score
weights and the S4 control mapping draw on the same source (see
memory/decisions.md). rule_id is the stable join key for S4.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from models import Finding, Resource, Severity

Detector = Callable[[Resource], "Finding | None"]

# rule_id -> (title, severity). Severity per AVD/CIS (documented in decisions.md).
RULES: dict[str, tuple[str, Severity]] = {
    "S3_PUBLIC_BUCKET": ("Publicly accessible S3 bucket", "high"),
    "OPEN_SSH": ("Security group allows SSH from 0.0.0.0/0", "critical"),
    "UNENCRYPTED_STORAGE": ("Storage resource is not encrypted at rest", "high"),
    "PUBLIC_DB": ("Database instance is publicly accessible", "high"),
}

_WORLD_CIDRS = {"0.0.0.0/0", "::/0"}
_PUBLIC_ACLS = {"public-read", "public-read-write", "PublicRead", "PublicReadWrite"}
_S3_BUCKET_TYPES = {"aws_s3_bucket", "AWS::S3::Bucket"}
_S3_POLICY_TYPES = {"aws_s3_bucket_policy", "AWS::S3::BucketPolicy"}
_ENCRYPTION_ATTR = {
    "aws_ebs_volume": "encrypted",
    "aws_db_instance": "storage_encrypted",
    "AWS::EC2::Volume": "Encrypted",
    "AWS::RDS::DBInstance": "StorageEncrypted",
}
_PUBLIC_ACCESS_ATTR = {
    "aws_db_instance": "publicly_accessible",
    "AWS::RDS::DBInstance": "PubliclyAccessible",
}


def _finding(resource: Resource, rule_id: str, evidence: str) -> Finding:
    title, severity = RULES[rule_id]
    return Finding(
        rule_id=rule_id,
        title=title,
        severity=severity,
        resource_type=resource.type,
        resource_name=resource.name,
        file=resource.file,
        line=resource.line,
        evidence=evidence,
    )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _to_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _is_false(value: Any) -> bool:
    return value is False or (isinstance(value, str) and value.strip().lower() == "false")


def _is_true(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


# --- S3 public bucket ------------------------------------------------------

def _principal_is_wildcard(principal: Any) -> bool:
    if principal == "*":
        return True
    if isinstance(principal, dict):
        for value in principal.values():
            if value == "*" or (isinstance(value, list) and "*" in value):
                return True
    return False


def _statement_is_public(statement: dict[str, Any]) -> bool:
    if statement.get("Effect") != "Allow":
        return False
    # A scoping Condition (e.g. aws:SourceIp / aws:SourceVpce) makes the
    # wildcard principal non-public — this is the exact Checkov false positive.
    if statement.get("Condition"):
        return False
    return _principal_is_wildcard(statement.get("Principal"))


def _strip_heredoc(text: str) -> str:
    """hcl2 keeps heredoc markers (`<<TAG` … `TAG`) around the body; drop them."""
    body = text.strip()
    if body.startswith("<<"):
        lines = body.split("\n")
        if len(lines) >= 2:
            return "\n".join(lines[1:-1])
    return text


def _policy_is_public(policy: Any) -> bool:
    if isinstance(policy, str):
        try:
            policy = json.loads(_strip_heredoc(policy))
        except (ValueError, TypeError):
            return False
    if not isinstance(policy, dict):
        return False
    statements = policy.get("Statement")
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list):
        return False
    return any(_statement_is_public(s) for s in statements if isinstance(s, dict))


def detect_public_s3(resource: Resource) -> Finding | None:
    attrs = resource.attributes
    if resource.type in _S3_BUCKET_TYPES:
        acl = attrs.get("acl") or attrs.get("AccessControl")
        if isinstance(acl, str) and acl in _PUBLIC_ACLS:
            return _finding(resource, "S3_PUBLIC_BUCKET", f"ACL '{acl}' grants public access")
        if _policy_is_public(attrs.get("policy")):
            return _finding(
                resource,
                "S3_PUBLIC_BUCKET",
                "bucket policy allows a wildcard principal with no scoping condition",
            )
    if resource.type in _S3_POLICY_TYPES:
        if _policy_is_public(attrs.get("policy") or attrs.get("PolicyDocument")):
            return _finding(
                resource,
                "S3_PUBLIC_BUCKET",
                "bucket policy allows a wildcard principal with no scoping condition",
            )
    return None


# --- Open SSH --------------------------------------------------------------

def _ssh_open(rule: Any, cidr_key: str, from_key: str, to_key: str) -> bool:
    if not isinstance(rule, dict):
        return False
    cidrs = rule.get(cidr_key)
    if isinstance(cidrs, list):
        cidr_set = {c for c in cidrs if isinstance(c, str)}
    elif isinstance(cidrs, str):
        cidr_set = {cidrs}
    else:
        cidr_set = set()
    if not (cidr_set & _WORLD_CIDRS):
        return False
    start, end = _to_int(rule.get(from_key)), _to_int(rule.get(to_key))
    if start is None or end is None:
        return False
    return start <= 22 <= end


def detect_open_ssh(resource: Resource) -> Finding | None:
    if resource.type == "aws_security_group":
        spec = ("cidr_blocks", "from_port", "to_port", "ingress")
    elif resource.type == "AWS::EC2::SecurityGroup":
        spec = ("CidrIp", "FromPort", "ToPort", "SecurityGroupIngress")
    else:
        return None
    cidr_key, from_key, to_key, ingress_key = spec
    for rule in _as_list(resource.attributes.get(ingress_key)):
        if _ssh_open(rule, cidr_key, from_key, to_key):
            return _finding(
                resource, "OPEN_SSH", "ingress permits TCP 22 from 0.0.0.0/0"
            )
    return None


# --- Unencrypted storage ---------------------------------------------------

def detect_unencrypted_storage(resource: Resource) -> Finding | None:
    attr = _ENCRYPTION_ATTR.get(resource.type)
    if attr is None:
        return None
    if _is_false(resource.attributes.get(attr)):
        return _finding(
            resource, "UNENCRYPTED_STORAGE", f"{attr} is false — storage unencrypted at rest"
        )
    return None


# --- Public database -------------------------------------------------------

def detect_public_db(resource: Resource) -> Finding | None:
    attr = _PUBLIC_ACCESS_ATTR.get(resource.type)
    if attr is None:
        return None
    if _is_true(resource.attributes.get(attr)):
        return _finding(
            resource, "PUBLIC_DB", f"{attr} is true — database reachable from the internet"
        )
    return None


DETECTORS: list[Detector] = [
    detect_public_s3,
    detect_open_ssh,
    detect_unencrypted_storage,
    detect_public_db,
]
