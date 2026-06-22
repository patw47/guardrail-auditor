"""CloudFormation (YAML/JSON) parser → normalized resources.

One PyYAML SafeLoader subclass handles both formats (YAML is a superset of
JSON, so `.json` parses through the same path and gets line numbers for free)
and tolerates CFN intrinsic tags (`!Ref`, `!GetAtt`, `!Sub`, …) by turning them
into marker dicts so the loader never chokes. Values come from `yaml.load`;
per-resource line numbers come from the composed node tree (`yaml.compose`),
which points at the real logical-id key and so survives leading comments.
"""

from __future__ import annotations

from typing import Any

import yaml

from models import Resource

from .errors import ParseError


class _CfnLoader(yaml.SafeLoader):
    """Isolated loader so the intrinsic-tag constructors don't leak globally."""


def _construct_intrinsic(loader: Any, tag_suffix: str, node: Any) -> dict[str, Any]:
    key = tag_suffix if tag_suffix in ("Ref", "Condition") else f"Fn::{tag_suffix}"
    if isinstance(node, yaml.ScalarNode):
        value: Any = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    else:
        value = loader.construct_mapping(node, deep=True)
    return {key: value}


_CfnLoader.add_multi_constructor("!", _construct_intrinsic)


def _resource_lines(root: Any) -> dict[str, int]:
    """1-based line of each logical id, read from the composed node tree."""
    out: dict[str, int] = {}
    if not isinstance(root, yaml.MappingNode):
        return out
    for key_node, value_node in root.value:
        if getattr(key_node, "value", None) == "Resources" and isinstance(
            value_node, yaml.MappingNode
        ):
            for lid_node, _body_node in value_node.value:
                out[str(lid_node.value)] = lid_node.start_mark.line + 1
    return out


def parse(content: str, filename: str) -> list[Resource]:
    """Parse CloudFormation YAML or JSON content into normalized resources."""
    try:
        data = yaml.load(content, Loader=_CfnLoader)  # noqa: S506 - subclassed SafeLoader
        root = yaml.compose(content, Loader=_CfnLoader)
    except yaml.YAMLError as exc:
        raise ParseError(
            f"{filename}: invalid CloudFormation YAML/JSON ({exc.__class__.__name__})"
        ) from exc

    if data is None:
        return []
    if not isinstance(data, dict):
        raise ParseError(f"{filename}: CloudFormation template must be a mapping")

    resources_data = data.get("Resources")
    if not isinstance(resources_data, dict):
        return []

    lines = _resource_lines(root)
    resources: list[Resource] = []
    for logical_id, body in resources_data.items():
        if not isinstance(body, dict):
            continue
        rtype = body.get("Type")
        if not isinstance(rtype, str):
            continue
        props = body.get("Properties", {})
        attributes = props if isinstance(props, dict) else {}
        resources.append(
            Resource(
                format="cloudformation",
                type=rtype,
                name=str(logical_id),
                attributes=attributes,
                file=filename,
                line=lines.get(str(logical_id), 1),
            )
        )
    return resources
