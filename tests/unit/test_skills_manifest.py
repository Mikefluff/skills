"""skills.json validates against the schema it points at.

Line 2 of the manifest has always carried a `$schema` URL. Until this test was
written the file it named did not exist, so every editor that fetched it got a
404 and the manifest was validated by nothing at all — which is how a `deps`
entry came to hold a directory path, and how `layer` and `tags` grew their
vocabularies by accident rather than by decision.

The validator here covers only the constructs the schema actually uses, and a
test asserts it stays that way. Depending on `jsonschema` would either add a
runtime dependency to a suite that has none, or skip in CI — and a gate that
skips is the failure mode this release spent its time removing.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MANIFEST = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "docs" / "skills.schema.json").read_text(encoding="utf-8"))

SUPPORTED = {
    "$schema", "$id", "$ref", "$defs", "title", "description",
    "type", "required", "properties", "additionalProperties",
    "items", "enum", "pattern", "minLength", "minItems", "uniqueItems",
}

TYPES = {"object": dict, "array": list, "string": str, "number": float, "integer": int}


def _object_errors(value, schema, path, defs) -> list[str]:
    errors = [f"{path}: missing required property {k!r}" for k in schema.get("required", []) if k not in value]
    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        errors += [f"{path}: unexpected property {k!r}" for k in value if k not in properties]
    for key, sub in properties.items():
        if key in value:
            errors += validate(value[key], sub, f"{path}.{key}", defs)
    return errors


def _array_errors(value, schema, path, defs) -> list[str]:
    errors = []
    if len(value) < schema.get("minItems", 0):
        errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
    if schema.get("uniqueItems") and len(value) != len(set(map(str, value))):
        errors.append(f"{path}: items must be unique")
    for i, item in enumerate(value):
        errors += validate(item, schema.get("items", {}), f"{path}[{i}]", defs)
    return errors


def _string_errors(value, schema, path) -> list[str]:
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if len(value) < schema.get("minLength", 0):
        errors.append(f"{path}: shorter than {schema['minLength']} characters")
    return errors


def validate(value, schema, path="$", defs=None) -> list[str]:
    """Return every way `value` fails `schema`. Empty list means valid."""
    defs = defs if defs is not None else schema.get("$defs", {})
    if "$ref" in schema:
        return validate(value, defs[schema["$ref"].removeprefix("#/$defs/")], path, defs)

    expected = schema.get("type")
    if expected and not isinstance(value, TYPES[expected]):
        return [f"{path}: expected {expected}, got {type(value).__name__}"]

    if expected == "object":
        return _object_errors(value, schema, path, defs)
    if expected == "array":
        return _array_errors(value, schema, path, defs)
    if expected == "string":
        return _string_errors(value, schema, path)
    return []


def _keywords(node) -> set[str]:
    if isinstance(node, dict):
        return set(node) | {k for v in node.values() for k in _keywords(v)}
    if isinstance(node, list):
        return {k for v in node for k in _keywords(v)}
    return set()


class TestManifest(unittest.TestCase):
    def test_manifest_validates(self):
        errors = validate(MANIFEST, SCHEMA)
        self.assertEqual([], errors, "\n" + "\n".join(errors))

    def test_the_validator_understands_the_whole_schema(self):
        # Property names and enum members are data, not keywords — only the
        # nodes that describe structure are checked here.
        structural = _keywords(
            {k: v for k, v in SCHEMA.items() if k != "properties"}
        ) - _known_data_keys()
        unsupported = structural - SUPPORTED
        self.assertEqual(
            set(),
            unsupported,
            f"schema uses {sorted(unsupported)}, which this validator ignores — "
            f"a constraint nothing enforces is worse than none",
        )

    def test_version_tracks_the_release(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), MANIFEST["version"])

    def test_declared_id_matches_where_the_manifest_looks_for_it(self):
        self.assertEqual(MANIFEST["$schema"], SCHEMA["$id"])


class TestDeps(unittest.TestCase):
    def test_every_dep_resolves(self):
        names = {s["name"] for s in MANIFEST["skills"]}
        for skill in MANIFEST["skills"]:
            for dep in skill.get("deps", []):
                with self.subTest(skill=skill["name"], dep=dep):
                    self.assertTrue(
                        dep in names or (ROOT / dep).exists(),
                        f"{skill['name']} depends on {dep!r}, which is neither a "
                        f"registered skill nor a path in the repo",
                    )


def _known_data_keys() -> set[str]:
    """Property names and $defs keys, which share a namespace with keywords."""
    data: set[str] = set(SCHEMA.get("$defs", {}))
    for node in (SCHEMA, *SCHEMA.get("$defs", {}).values()):
        data |= set(node.get("properties", {}))
        for sub in node.get("properties", {}).values():
            data |= set(sub.get("properties", {}))
    return data


if __name__ == "__main__":
    unittest.main()
