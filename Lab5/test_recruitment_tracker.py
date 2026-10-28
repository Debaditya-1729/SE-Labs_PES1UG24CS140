"""Regression tests for the cleaned recruitment tracker."""

import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import recruitment_tracker as tracker


class RecruitmentTrackerTests(unittest.TestCase):
    """Exercise the original workflow and repaired edge cases."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE applicants (id INTEGER PRIMARY KEY, name TEXT, "
            "role TEXT, expected_salary INTEGER, status TEXT)"
        )
        self.connection_patch = patch.object(tracker, "conn", self.connection)
        self.connection_patch.start()
        self.addCleanup(self.connection.close)
        self.addCleanup(self.connection_patch.stop)

    def test_shortlist_preserves_demo_arithmetic(self):
        tracker.add_applicant("Nina", "analyst", 600000)
        tracker.add_applicant("Omar", "analyst", 750000)
        self.assertEqual(
            tracker.shortlist("analyst", "500000 + 150000"), ["Nina"]
        )

    def test_shortlist_includes_salary_boundary(self):
        tracker.add_applicant("Nina", "analyst", 650000)
        self.assertEqual(tracker.shortlist("analyst", "650000"), ["Nina"])

    def test_shortlist_returns_empty_list(self):
        tracker.add_applicant("Nina", "analyst", 600000)
        self.assertEqual(tracker.shortlist("analyst", "1"), [])
        self.assertEqual(tracker.shortlist("unknown", "900000"), [])

    def test_shortlist_filters_role(self):
        tracker.add_applicant("Priya", "developer", 100)
        self.assertEqual(tracker.shortlist("analyst", "1000"), [])

    def test_parameterized_insert_accepts_apostrophes(self):
        tracker.add_applicant("O'Connor", "analyst's role", 123, "HR's review")
        row = self.connection.execute(
            "SELECT name, role, expected_salary, status FROM applicants"
        ).fetchone()
        self.assertEqual(
            row, ("O'Connor", "analyst's role", 123, "HR's review")
        )

    def test_status_update_and_count(self):
        tracker.add_applicant("Nina", "analyst", 600000)
        tracker.update_status(1, "interview")
        self.assertEqual(tracker.count_by_status("interview"), 1)
        self.assertEqual(tracker.count_by_status("applied"), 0)
        self.assertEqual(tracker.count_by_status("HR's review"), 0)

    def test_update_failure_is_not_silenced(self):
        self.connection.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            tracker.update_status(1, "interview")

    def test_failed_update_rolls_back(self):
        tracker.add_applicant("Nina", "analyst", 600000)
        self.connection.execute(
            "CREATE TRIGGER reject_update BEFORE UPDATE ON applicants "
            "BEGIN SELECT RAISE(ABORT, 'update rejected'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            tracker.update_status(1, "interview")
        self.assertEqual(tracker.count_by_status("applied"), 1)
        self.assertFalse(self.connection.in_transaction)

    def test_arithmetic_precedence_and_unary_signs(self):
        self.assertEqual(tracker.parse_salary_rule("(5 + 3) * 2 / 4"), 4)
        self.assertEqual(tracker.parse_salary_rule("-5 + +10"), 5)
        self.assertEqual(tracker.parse_salary_rule(" 650000 "), 650000)
        self.assertEqual(tracker.parse_salary_rule("1.5 + 2.5"), 4)

    def test_arithmetic_rejects_non_numeric_syntax(self):
        invalid = [
            "__import__('os')", "salary", "(1).__class__", "[1]",
            "True", "'500'", "2 ** 100", "1 // 2", "1 % 2", "1 << 2",
        ]
        for expression in invalid:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    tracker.parse_salary_rule(expression)

    def test_arithmetic_rejects_invalid_and_unbounded_input(self):
        for expression in ("", " ", "1 +", "1 / 0", "1e309", "1e13",
                           "1" * 129, None, 650000):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    tracker.parse_salary_rule(expression)

    def test_csv_round_trips_quotes_commas_unicode_and_newlines(self):
        name = 'Zoë, "Mira"\nO\'Connor'
        tracker.add_applicant(name, "R&D, analyst", 100)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "applicants.csv"
            handles = []
            real_open = open

            def track_open(*args, **kwargs):
                handle = real_open(*args, **kwargs)
                handles.append(handle)
                return handle

            with patch("builtins.open", side_effect=track_open):
                tracker.export_report(path)
            self.assertTrue(handles[0].closed)
            with path.open(encoding="utf-8", newline="") as report:
                self.assertEqual(
                    list(csv.reader(report)),
                    [[name, "R&D, analyst", "applied"]],
                )
            path.rename(Path(directory) / "renamed.csv")

    def test_export_failure_reaches_caller(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                tracker.export_report(directory)

    def test_import_does_not_run_demo_or_print(self):
        spec = importlib.util.spec_from_file_location(
            "isolated_tracker", Path(tracker.__file__)
        )
        module = importlib.util.module_from_spec(spec)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            spec.loader.exec_module(module)
        try:
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(module.count_by_status("applied"), 0)
        finally:
            module.conn.close()

    def test_main_script_preserves_original_output_and_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(Path(tracker.__file__).resolve())],
                cwd=directory, capture_output=True, text=True,
                check=True, timeout=10,
            )
            self.assertEqual(result.stdout, "['Nina']\n2 in interview\n")
            self.assertEqual(result.stderr, "")
            path = Path(directory) / "applicants_report.csv"
            with path.open(encoding="utf-8", newline="") as report:
                self.assertEqual(list(csv.reader(report)), [
                    ["Nina", "analyst", "interview"],
                    ["Omar", "analyst", "interview"],
                    ["Priya", "developer", "applied"],
                ])


if __name__ == "__main__":
    unittest.main()
