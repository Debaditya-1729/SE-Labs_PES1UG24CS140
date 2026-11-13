# Lab 7: Fuzzing for Input Validation Bugs

**Name:** Debaditya Chakrabarti  
**SRN:** PES1UG24CS140  
**Section:** C

## Files

- `library_fines.py` — fixed application, preserving the assigned module and function names.
- `test_processor.py` — completed Hypothesis and regression tests for all three functions.
- `Lab_7_Fuzz_Testing_Report.pdf` — original application, pre-fix failing tests, fixed application and passing tests, with terminal screenshots.
- `screenshots/` — the original terminal captures included in the report.

The handout uses the generic names `processor.py` and `test_processor.py`, but the [assigned Lab 7 repository](https://github.com/SETAPESU26/L6_L7_14_library_fines/tree/29fac1ace717b8855298f18d533d61e6e3615517/Lab%207) provides `library_fines.py` and an incomplete `test_library_fines.py`. The deliverable test file uses the handout's requested name and imports the actual assigned module. The three no-crash properties complete the intent of the starter scaffold; the remaining tests add functional and regression checks.

## Run

Using Python 3.10 or newer, from this folder:

```bash
python -m pip install -r requirements.txt
python library_fines.py
python -m pytest -q test_processor.py
```

The report was run with Python 3.13, pytest 9.2.0 and Hypothesis 6.170.15. Final result: **39 passed**. Six property tests use Hypothesis with up to 200 generated examples each; the test count is the number of pytest cases, not the number of generated examples. The initial screenshots show each of the three no-crash properties separately against the unchanged assigned application.

## Input contract and fixes

The source did not define invalid-input behavior, so the following explicit validation policy was adopted:

- All three functions accept strings only, at most 4,096 characters before trimming. Invalid values raise `ValueError`; the CLI catches it and exits with a concise message and status 1. Unexpected EOF is also handled.
- Member IDs have the form `letters-digits`, with ASCII letters and 1–9 ASCII digits. Leading/trailing whitespace is allowed; the returned type is uppercase and number is a nonnegative integer. The nine-digit bound is an explicit resource limit, not a rule stated by the assignment.
- Fine input is a nonempty comma-separated list of nonnegative day counts, each 1–9 ASCII digits, with surrounding whitespace allowed. Empty fields, signs, non-digits and oversized values are rejected. The original calculation remains 2 per day after day 14, per book.
- Titles must contain at least two whitespace-separated words. Their first characters are uppercased, preserving the original Unicode behavior (some uppercase characters expand to multiple characters).

The length and digit limits bound input work and numeric conversion; they do not imply protection from every denial-of-service or other vulnerability. Fuzzing improves confidence but cannot prove correctness or security.
