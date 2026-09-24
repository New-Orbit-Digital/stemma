"""Tests for tools/validate.py.

The validator is exercised through its CLI, the way CI and the packet's
acceptance checks call it.
"""

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

ERROR_RULES = ["E%02d" % n for n in range(1, 12)]
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
        self.assertEqual(self.summary(result.stdout), (6, 0, 0), result.stdout)

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
            "fixture-disputed",
            "fixture-stub-parent",
        ):
            self.assertIn(required, names)


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


class WarningTest(SummaryLineTest):
    def test_w1_is_reported_without_failing(self):
        result = run_validate("--path", os.path.join(WARN, "W1"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("W1", rule_ids(result.stdout), result.stdout)
        self.assertEqual(self.summary(result.stdout), (2, 0, 1), result.stdout)

    def test_w2_is_reported_without_failing(self):
        result = run_validate("--path", os.path.join(WARN, "W2"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("W2", rule_ids(result.stdout), result.stdout)
        self.assertEqual(self.summary(result.stdout), (1, 0, 1), result.stdout)


class CliTest(SummaryLineTest):
    def test_missing_directory_fails(self):
        result = run_validate("--path", os.path.join(FIXTURES, "does-not-exist"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.summary(result.stdout), (0, 1, 0), result.stdout)


if __name__ == "__main__":
    unittest.main()
