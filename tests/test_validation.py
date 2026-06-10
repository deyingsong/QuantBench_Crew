from quantbench_crew.skills.validation import extract_json_object, validate

SCHEMA = {
    "type": "object",
    "required": ["name", "level"],
    "properties": {
        "name": {"type": "string"},
        "level": {"type": "string", "enum": ["low", "high"]},
        "score": {"type": ["number", "null"]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}


def test_valid_payload_has_no_errors() -> None:
    payload = {"name": "x", "level": "low", "score": None, "tags": ["a"]}

    assert validate(payload, SCHEMA) == []


def test_missing_required_and_bad_enum_reported_with_paths() -> None:
    errors = validate({"level": "medium"}, SCHEMA)

    assert any("missing required key 'name'" in error for error in errors)
    assert any("$.level" in error and "not in" in error for error in errors)


def test_wrong_types_reported() -> None:
    errors = validate({"name": 3, "level": "low", "tags": [1]}, SCHEMA)

    assert any("$.name: expected type string" in error for error in errors)
    assert any("$.tags[0]: expected type string" in error for error in errors)


def test_booleans_are_not_numbers() -> None:
    assert validate(True, {"type": "number"}) != []
    assert validate(1.5, {"type": "number"}) == []


def test_extract_json_object_handles_fences_and_prose() -> None:
    fenced = '```json\n{"a": 1}\n```'
    prose = 'Here is the result: {"a": 1} as requested.'

    assert extract_json_object(fenced) == {"a": 1}
    assert extract_json_object(prose) == {"a": 1}
    assert extract_json_object("no json here") == {}
    assert extract_json_object("[1, 2]") == {}
