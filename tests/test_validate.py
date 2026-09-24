"""Tests for tools/validate.py.

The validator is exercised through its CLI, the way CI and the packet's
acceptance checks call it.
"""

import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATE = os.path.join(ROOT, "tools", "validate.py")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
VALID = os.path.join(FIXTURES, "valid")
INVALID = os.path.join(FIXTURES, "invalid")
WARN = os.path.join(FIXTURES, "warn")

# E07 (the v1 lineage.status table) and E08 (per-claim evidence) are retired
# rules, not gaps: docs/schema.md, "Errors".
ERROR_RULES = [
    "E01",
    "E02",
    "E03",
    "E04",
    "E05",
    "E06",
    "E09",
    "E10",
    "E11",
    "E12",
    "E13",
    "E14",
]
WARN_RULES = ["W1", "W3"]
RULE_RE = re.compile(r"^(E\d{2}|W\d)\b", re.MULTILINE)
SUMMARY_RE = re.compile(r"^(\d+) cards, (\d+) errors, (\d+) warnings$")


def run_validate(*args):
    return subprocess.run(
        [sys.executable, VALIDATE, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def rule_ids(output):
    return set(RULE_RE.findall(output))


def error_ids(output):
    return {rule for rule in rule_ids(output) if rule.startswith("E")}


class SummaryLineTest(unittest.TestCase):
    def summary(self, output):
        lines = output.strip().splitlines()
        self.assertTrue(lines, "validator printed nothing")
        match = SUMMARY_RE.match(lines[-1])
        self.assertIsNotNone(match, "last line is not a summary: %r" % lines[-1])
        return tuple(int(value) for value in match.groups())


class RealCatalogTest(SummaryLineTest):
    def test_real_catalog_is_valid(self):
        result = run_validate()
        cards, errors, _warnings = self.summary(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(errors, 0, result.stdout)
        self.assertGreaterEqual(cards, 0)


class ValidFixturesTest(SummaryLineTest):
    def test_valid_fixtures_pass(self):
        result = run_validate("--path", VALID)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.summary(result.stdout), (7, 0, 0), result.stdout)

    def test_valid_fixtures_cover_the_required_shapes(self):
        names = sorted(
            os.path.splitext(name)[0]
            for name in os.listdir(VALID)
            if name.endswith(".json")
        )
        self.assertGreaterEqual(len(names), 5)
        for name in names:
            self.assertTrue(name.startswith("fixture-"), name)
        for required in (
            "fixture-landrace-root",
            "fixture-known-cross",
            "fixture-partial",
            "fixture-reviewed",
            "fixture-stub-parent",
            "fixture-links",
        ):
            self.assertIn(required, names)

    def test_a_fixture_summary_uses_every_markup_form(self):
        with open(
            os.path.join(VALID, "fixture-links.json"), "r", encoding="utf-8"
        ) as handle:
            summary = json.load(handle)["summary"]
        for form in (
            "[[fixture-landrace-root]]",
            "[[fixture-known-cross|",
            "[[breeder:",
            "[[kind:",
            "[[country:",
            "[[label:",
        ):
            self.assertIn(form, summary)

    def test_markup_does_not_count_against_the_summary_limit(self):
        """The fixture's raw text is over 400; its visible text is not."""
        with open(
            os.path.join(VALID, "fixture-links.json"), "r", encoding="utf-8"
        ) as handle:
            summary = json.load(handle)["summary"]
        self.assertGreater(len(summary), 400)
        result = run_validate("--path", VALID)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("E11", result.stdout)

    def test_valid_fixtures_cover_every_source_category(self):
        seen = set()
        for name in os.listdir(VALID):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(VALID, name), "r", encoding="utf-8") as handle:
                card = json.load(handle)
            for source in card.get("sources") or []:
                seen.add(source.get("category"))
        self.assertEqual(seen, {"breeder", "publication", "database", "community"})


class InvalidFixturesTest(SummaryLineTest):
    def test_every_rule_has_a_fixture_directory(self):
        self.assertEqual(sorted(os.listdir(INVALID)), ERROR_RULES)

    def test_each_invalid_fixture_reports_only_its_rule(self):
        for rule in ERROR_RULES:
            with self.subTest(rule=rule):
                result = run_validate("--path", os.path.join(INVALID, rule))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(rule, rule_ids(result.stdout), result.stdout)
                self.assertEqual(error_ids(result.stdout), {rule}, result.stdout)
                _cards, errors, _warnings = self.summary(result.stdout)
                self.assertGreater(errors, 0, result.stdout)

    def test_every_reported_line_starts_with_a_rule_id(self):
        for rule in ERROR_RULES:
            with self.subTest(rule=rule):
                result = run_validate("--path", os.path.join(INVALID, rule))
                for line in result.stdout.strip().splitlines()[:-1]:
                    self.assertRegex(line, RULE_RE)

    def test_cycle_path_is_reported(self):
        result = run_validate("--path", os.path.join(INVALID, "E06"))
        self.assertIn("lineage cycle:", result.stdout)
        self.assertIn("fixture-e06-a", result.stdout)
        self.assertIn("fixture-e06-b", result.stdout)

    def test_missing_parent_message_names_the_parent(self):
        result = run_validate("--path", os.path.join(INVALID, "E05"))
        self.assertIn("parent 'fixture-e05-ghost' not found", result.stdout)

    def test_bad_source_category_names_the_value(self):
        result = run_validate("--path", os.path.join(INVALID, "E04"))
        self.assertIn("'hearsay'", result.stdout)

    def test_over_length_is_measured_on_the_visible_text(self):
        result = run_validate("--path", os.path.join(INVALID, "E11"))
        self.assertIn("visible characters, over the 400 limit", result.stdout)
        # The card whose length is only over once the markup is reduced.
        self.assertIn("fixture-e11-long-visible-text.json", result.stdout)

    def test_malformed_markup_names_what_is_wrong(self):
        result = run_validate("--path", os.path.join(INVALID, "E12"))
        for message in (
            "unbalanced '[['",
            "unknown link prefix 'strain:'",
            "empty link target",
        ):
            self.assertIn(message, result.stdout)

    def test_an_unresolved_link_names_its_target(self):
        result = run_validate("--path", os.path.join(INVALID, "E13"))
        for message in (
            "[[fixture-e13-ghost]] names no card",
            "[[breeder:Nobody Seeds]] matches no card's 'breeder' exactly",
            "[[country:ZZ|Nowhere]] is not a country in tools/countries.py",
            "[[country:JM|Jamaica]] matches no card's 'origin.country'",
            "[[kind:sativa|sativa]] is not one of",
            "[[label:landrace|landrace]] is not one of",
        ):
            self.assertIn(message, result.stdout)

    def test_an_unknown_country_code_names_the_code_and_the_map(self):
        result = run_validate("--path", os.path.join(INVALID, "E14"))
        self.assertIn("origin.country 'ZZ' is not in tools/countries.py", result.stdout)


class WarningTest(SummaryLineTest):
    def test_every_warning_has_a_fixture_directory(self):
        self.assertEqual(sorted(os.listdir(WARN)), WARN_RULES)

    def test_w1_is_reported_without_failing(self):
        result = run_validate("--path", os.path.join(WARN, "W1"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("W1", rule_ids(result.stdout), result.stdout)
        self.assertEqual(self.summary(result.stdout), (2, 0, 1), result.stdout)

    def test_w3_is_reported_without_failing(self):
        result = run_validate("--path", os.path.join(WARN, "W3"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("W3", rule_ids(result.stdout), result.stdout)
        self.assertIn("landrace", result.stdout)
        self.assertEqual(self.summary(result.stdout), (2, 0, 1), result.stdout)


class CliTest(SummaryLineTest):
    def test_missing_directory_fails(self):
        result = run_validate("--path", os.path.join(FIXTURES, "does-not-exist"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.summary(result.stdout), (0, 1, 0), result.stdout)


if __name__ == "__main__":
    unittest.main()
