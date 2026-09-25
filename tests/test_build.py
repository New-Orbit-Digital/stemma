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
                "fixture-chemotype",
                "fixture-chemotype-terpenes",
                "fixture-cut",
                "fixture-known-cross",
                "fixture-landrace-root",
                "fixture-links",
                "fixture-partial",
                "fixture-reviewed",
                "fixture-stub-parent",
            ],
        )

    def test_summary_keeps_its_markup_and_gains_the_visible_text(self):
        """``summary`` is the source of truth; ``summary_plain`` is what reads."""
        data = json.loads(self.build_valid())
        cards = {strain["id"]: strain for strain in data["strains"]}
        card = cards["fixture-links"]
        self.assertIn("[[fixture-landrace-root]]", card["summary"])
        self.assertNotIn("[[", card["summary_plain"])
        self.assertIn("Fixture Landrace", card["summary_plain"])  # the card's name
        self.assertIn("the known cross fixture", card["summary_plain"])  # link text
        self.assertLessEqual(len(card["summary_plain"]), 400)
        self.assertGreater(len(card["summary"]), 400)
        # Every card that says something carries both, and no more than that.
        for strain in data["strains"]:
            if strain.get("summary"):
                self.assertIn("summary_plain", strain, strain["id"])
            else:
                self.assertNotIn("summary_plain", strain, strain["id"])

    def test_summary_plain_is_the_summary_when_there_is_no_markup(self):
        data = json.loads(self.build_valid())
        for strain in data["strains"]:
            if strain.get("summary") and "[[" not in strain["summary"]:
                self.assertEqual(strain["summary_plain"], strain["summary"])

    def test_a_chemotype_rides_along_as_written(self):
        """Additive, so the dataset is still schema_version 2."""
        data = json.loads(self.build_valid())
        self.assertEqual(data["schema_version"], 2)
        cards = {strain["id"]: strain for strain in data["strains"]}
        chemotype = cards["fixture-chemotype"]["chemotype"]
        self.assertEqual(chemotype["thc"]["display"], "18–24%")
        self.assertEqual(
            [entry["name"] for entry in chemotype["dominant_terpenes"]],
            ["myrcene", "limonene", "caryophyllene"],
        )
        self.assertEqual(chemotype["dominant_terpenes"][0]["percent"], 0.35)
        # A card that does not carry one does not gain the key.
        self.assertNotIn("chemotype", cards["fixture-reviewed"])

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
