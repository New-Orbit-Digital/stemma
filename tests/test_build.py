"""Tests for tools/build.py — the compiled dataset (the Budlogs seam)."""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tools", "build.py")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
VALID = os.path.join(FIXTURES, "valid")

GENERATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

EXPECTED_EDGES = [
    {"child": "fixture-cut", "parent": "fixture-reviewed"},
    {"child": "fixture-known-cross", "parent": "fixture-landrace-root"},
    {"child": "fixture-known-cross", "parent": "fixture-stub-parent"},
    {"child": "fixture-partial", "parent": "fixture-known-cross"},
    {"child": "fixture-reviewed", "parent": "fixture-known-cross"},
]


def run_build(path, out):
    """Build into the output directory ``out`` (the site root)."""
    return subprocess.run(
        [sys.executable, BUILD, "--path", path, "--out", out],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def dataset_path(out):
    return os.path.join(out, "data", "stemma.json")


class BuildTest(unittest.TestCase):
    def build_valid(self, name="site"):
        out = os.path.join(self.tmp.name, name)
        result = run_build(VALID, out)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(dataset_path(out), "r", encoding="utf-8") as handle:
            return handle.read()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_dataset_shape(self):
        data = json.loads(self.build_valid())
        self.assertEqual(data["schema_version"], 2)
        self.assertRegex(data["generated"], GENERATED_RE)
        self.assertEqual(sorted(data), ["edges", "generated", "schema_version", "strains"])

    def test_strains_are_every_card_sorted_by_id(self):
        data = json.loads(self.build_valid())
        ids = [strain["id"] for strain in data["strains"]]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(
            ids,
            [
                "fixture-cut",
                "fixture-known-cross",
                "fixture-landrace-root",
                "fixture-partial",
                "fixture-reviewed",
                "fixture-stub-parent",
            ],
        )

    def test_edges_are_child_parent_pairs_sorted(self):
        data = json.loads(self.build_valid())
        self.assertEqual(data["edges"], EXPECTED_EDGES)
        keys = [(e["child"], e["parent"]) for e in data["edges"]]
        self.assertEqual(keys, sorted(keys))
        for edge in data["edges"]:
            self.assertEqual(sorted(edge), ["child", "parent"])

    def test_output_is_deterministic_apart_from_generated(self):
        first = self.build_valid("first")
        second = self.build_valid("second")
        self.assertEqual(strip_generated(first), strip_generated(second))
        one, two = json.loads(first), json.loads(second)
        one.pop("generated")
        two.pop("generated")
        self.assertEqual(one, two)

    def test_build_creates_missing_directories(self):
        out = os.path.join(self.tmp.name, "nested", "dist")
        result = run_build(VALID, out)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(os.path.isfile(dataset_path(out)))

    def test_build_aborts_when_validation_fails(self):
        out = os.path.join(self.tmp.name, "site")
        result = run_build(os.path.join(FIXTURES, "invalid", "E05"), out)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("E05", result.stdout)
        self.assertFalse(os.path.exists(dataset_path(out)))

    def test_build_tolerates_warnings(self):
        out = os.path.join(self.tmp.name, "site")
        result = run_build(os.path.join(FIXTURES, "warn", "W1"), out)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("W1", result.stdout)
        self.assertTrue(os.path.isfile(dataset_path(out)))


def strip_generated(text):
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith('"generated"')
    )


if __name__ == "__main__":
    unittest.main()
