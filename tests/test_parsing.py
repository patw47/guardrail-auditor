"""S1: parsers → normalized resources. Both formats, line accuracy, edge cases."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.parsing import ParseError, parse_file
from models import Resource

FIX = Path(__file__).parent / "fixtures"
TF = FIX / "terraform"
CFN = FIX / "cloudformation"


def _by_name(resources: list[Resource]) -> dict[str, Resource]:
    return {r.name: r for r in resources}


def test_terraform_multi_resource_lines() -> None:
    by = _by_name(parse_file(TF / "commented_multi.tf"))
    assert set(by) == {"public_bucket", "open_ssh"}
    assert by["public_bucket"].format == "terraform"
    assert by["public_bucket"].type == "aws_s3_bucket"
    # line survives the leading #, //, /* */ comments and blank lines
    assert by["public_bucket"].line == 6
    assert by["open_ssh"].type == "aws_security_group"
    assert by["open_ssh"].line == 14
    # scalar strings are unquoted
    assert by["public_bucket"].attributes["acl"] == "public-read"


def test_terraform_nested_block_always_list() -> None:
    by = _by_name(parse_file(TF / "ingress_shapes.tf"))
    single = by["single"].attributes["ingress"]
    multi = by["multi"].attributes["ingress"]
    # same shape regardless of count: always a list (length 1 for a single block)
    assert isinstance(single, list) and len(single) == 1
    assert isinstance(multi, list) and len(multi) == 2
    assert all(isinstance(block, dict) for block in [*single, *multi])


def test_cfn_yaml_resources_lines() -> None:
    by = _by_name(parse_file(CFN / "template.yaml"))
    assert by["MyBucket"].format == "cloudformation"
    assert by["MyBucket"].type == "AWS::S3::Bucket"
    # logical-id line survives the leading comment
    assert by["MyBucket"].line == 7
    assert by["MySG"].line == 13
    # intrinsic !Ref handled (not a crash) and normalized to a marker dict
    assert by["MyBucket"].attributes["BucketName"] == {"Ref": "BucketNameParam"}


def test_cfn_json_matches_yaml() -> None:
    yaml_res = _by_name(parse_file(CFN / "template.yaml"))
    json_res = _by_name(parse_file(CFN / "template.json"))
    assert set(yaml_res) == set(json_res)
    for name, yr in yaml_res.items():
        jr = json_res[name]
        assert (yr.type, yr.attributes) == (jr.type, jr.attributes)
        assert jr.line > 0


def test_malformed_terraform_raises() -> None:
    with pytest.raises(ParseError):
        parse_file(TF / "malformed.tf")


def test_malformed_cloudformation_raises() -> None:
    with pytest.raises(ParseError):
        parse_file(CFN / "malformed.yaml")


def test_empty_or_comments_only_yields_zero() -> None:
    assert parse_file(TF / "empty.tf") == []
    assert parse_file(CFN / "comments_only.yaml") == []


def test_determinism() -> None:
    first = parse_file(TF / "commented_multi.tf")
    second = parse_file(TF / "commented_multi.tf")
    assert first == second
