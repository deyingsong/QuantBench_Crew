"""Minimal JSON-schema-subset validator for skill payloads.

Supports the subset the extraction skills need — ``type`` (including type
lists), ``required``, ``properties``, ``items``, and ``enum`` — without
adding a jsonschema dependency. Returns human-readable error strings rather
than raising, so skills can downgrade to their deterministic fallback and
record why.
"""

from __future__ import annotations

import json
from typing import Any

_TYPE_CHECKS = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "null": lambda value: value is None,
}


def validate(payload: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate ``payload`` against the schema subset; return error messages."""

    errors: list[str] = []

    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not any(_TYPE_CHECKS[type_name](payload) for type_name in allowed):
            errors.append(f"{path}: expected type {' or '.join(allowed)}")
            return errors  # deeper checks are meaningless on the wrong type

    if "enum" in schema and payload not in schema["enum"]:
        errors.append(f"{path}: {payload!r} not in {schema['enum']!r}")

    if isinstance(payload, dict):
        for key in schema.get("required", []):
            if key not in payload:
                errors.append(f"{path}: missing required key {key!r}")
        for key, subschema in schema.get("properties", {}).items():
            if key in payload:
                errors.extend(validate(payload[key], subschema, f"{path}.{key}"))

    if isinstance(payload, list) and "items" in schema:
        for index, item in enumerate(payload):
            errors.extend(validate(item, schema["items"], f"{path}[{index}]"))

    return errors


def extract_json_object(text: str) -> dict[str, Any]:
    """Best-effort extraction of a JSON object from LLM output text.

    Tolerates code fences and surrounding prose; returns {} when no object
    can be parsed so callers fall through to their deterministic fallback.
    """

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()

    candidates = [stripped]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and start < end:
        candidates.append(stripped[start : end + 1])

    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}
