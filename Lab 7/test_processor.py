"""Hypothesis fuzz and regression tests for the Lab 7 library processor.

The assigned repository calls the application library_fines.py rather than
processor.py; these tests exercise its three original public functions.
"""
import string

import pytest
from hypothesis import given, settings, strategies as st

from library_fines import parse_member_id, shelf_code, total_fine

FUZZ = settings(max_examples=200, derandomize=True, deadline=None,
                report_multiple_bugs=False)
ANY_INPUT = st.one_of(st.none(), st.text(max_size=100), st.integers(),
                      st.lists(st.integers(), max_size=3))


@FUZZ
@given(ANY_INPUT)
def test_parse_member_id_no_crash(value):
    try:
        result = parse_member_id(value)
    except ValueError:
        return  # Invalid input is rejected in a controlled way.
    assert isinstance(result, tuple) and len(result) == 2
    member, number = result
    assert isinstance(member, str) and member.isascii() and member.isalpha()
    assert member == member.upper()
    assert type(number) is int and 0 <= number <= 999_999_999


@FUZZ
@given(ANY_INPUT)
def test_total_fine_no_crash(value):
    try:
        result = total_fine(value)
    except ValueError:
        return
    assert type(result) is int and result >= 0


@FUZZ
@given(ANY_INPUT)
def test_shelf_code_no_crash(value):
    try:
        result = shelf_code(value)
    except ValueError:
        return
    assert isinstance(result, str) and result
    words = value.split()
    assert len(words) >= 2
    assert result == (words[0][0] + words[1][0]).upper()


@FUZZ
@given(st.text(alphabet=string.ascii_letters, min_size=1, max_size=30),
       st.integers(min_value=0, max_value=999_999_999))
def test_valid_member_ids(member, number):
    assert parse_member_id(f"{member}-{number}") == (member.upper(), number)


@FUZZ
@given(st.lists(st.integers(min_value=0, max_value=999_999_999),
                min_size=1, max_size=30))
def test_fine_matches_reference(days):
    csv = ", ".join(map(str, days))
    assert total_fine(csv) == sum(max(0, d - 14) * 2 for d in days)


@FUZZ
@given(st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
       st.text(alphabet=string.ascii_letters, min_size=1, max_size=20))
def test_shelf_code_for_valid_titles(first, second):
    assert shelf_code(first + "  " + second) == (first[0] + second[0]).upper()


@pytest.mark.parametrize("value", ["", "STU", "-1", "STU-", "STU--1", "STU-1-2",
                                   "STU--2", "STU-+1", "STU-1.5", "STU-١",
                                   "STU-1000000000", "S" * 4097 + "-1"])
def test_invalid_member_ids_are_rejected(value):
    with pytest.raises(ValueError):
        parse_member_id(value)


@pytest.mark.parametrize("value", ["", " ", "1,,3", ",1", "1,", "-1", "+1",
                                   "1.5", "١", "1000000000", "1," * 2049])
def test_invalid_days_are_rejected(value):
    with pytest.raises(ValueError):
        total_fine(value)


@pytest.mark.parametrize("value", ["", " ", "one", "a" * 4097, None, 123])
def test_invalid_titles_are_rejected(value):
    with pytest.raises(ValueError):
        shelf_code(value)


def test_boundaries_and_unicode_titles():
    assert parse_member_id(" stu-0007 ") == ("STU", 7)
    assert total_fine("0, 14, 15, 999999999") == 1_999_999_972
    assert shelf_code("  ßeta  東京  ") == "SS東"


def _run_cli(input_text):
    import subprocess
    import sys
    from pathlib import Path

    return subprocess.run(
        [sys.executable, str(Path(__file__).with_name("library_fines.py"))],
        input=input_text, text=True, capture_output=True, check=False,
    )


def test_cli_valid_input():
    result = _run_cli("STU-1023\n10,20,30\nThe Hobbit\n")
    assert result.returncode == 0
    assert "('STU', 1023)" in result.stdout
    assert "Total Fine: 44" in result.stdout
    assert "Shelf Code: TH" in result.stdout
    assert result.stderr == ""


def test_cli_rejects_invalid_input_without_traceback():
    result = _run_cli("STU--1\n")
    assert result.returncode == 1
    assert "Invalid input:" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_handles_end_of_input():
    result = _run_cli("")
    assert result.returncode == 1
    assert "Input ended" in result.stderr
    assert "Traceback" not in result.stderr
