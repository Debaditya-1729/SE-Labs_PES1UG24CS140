# Lab 5 — Static Code Analysis

| Field | Details |
|---|---|
| Student | Debaditya Chakrabarti |
| SRN | PES1UG24CS140 |
| Section | C |
| Assigned repository | https://github.com/SETAPESU26/L5_14_recruitment_tracker |
| Source commit | `a5dba868a578d85536d8c6b0ba7059961a7b47f0` |
| Assessed file | `recruitment_tracker.py` |
| Analysis date | 28 October 2026 |

## Verified results

| Check | Before | After |
|---|---:|---:|
| Pylint score | 4.47/10 | 10.00/10 |
| Pylint messages | 21 | 0 |
| Bandit findings | 3 (2 medium, 1 low; no high) | 0 |
| Flake8 findings | 8 | 0 |
| Regression tests | Not supplied upstream | 15 passed |

No findings were suppressed or rules disabled. The three analysis tools assess
**the assigned program**, not the preserved `.py.txt` original or the test file.
A clean report means no findings under these tool versions, not proof of the
absence of vulnerabilities or bugs. An empty final `flake8_report.txt` is the
expected successful result.

## Submission contents

- `recruitment_tracker.py` — cleaned, updated Python program.
- `issues.md` — 12 groups of tool-reported issues and their fixes, including
  original and final line references, severity where supplied by Bandit.
- `reflection.md` — four reflection responses. The supplied handout mentions
  reflection questions but does not enumerate them; the headings are explicitly
  identified as proposed prompts, not quoted handout questions.
- `reports/before/` and `reports/after/` — all six required raw scanner reports,
  original/final demonstration output, and the final regression test report.
- `Lab5_Static_Code_Analysis_Report.pdf` and `.docx` — formal report.
- `original/` — unmodified assigned code (stored as `.py.txt` to keep it out of
  recursive Python scans) and its upstream README.
- `test_recruitment_tracker.py` — 15 standard-library `unittest` tests.
- `requirements-dev.txt` — pinned analysis-tool environment.
- `run_analysis.sh` — reproducible final scans, exit statuses and tests.

## Reproduce

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python recruitment_tracker.py
bash run_analysis.sh
```

The recorded environment used CPython 3.13.15, Pylint 4.1.3, Bandit 1.9.4 and
Flake8 7.4.1. All three tools were run with their default checks; only Pylint's
persistence/cache was disabled for the final scan.

To reproduce the baseline separately, copy
`original/recruitment_tracker.py.txt` into an empty temporary folder as
`recruitment_tracker.py`, then run the three commands from the handout. Baseline
nonzero scanner exit statuses are expected because issues are present.

## Behaviour and design decisions

- The original demo still prints `['Nina']` and `2 in interview` and exports the
  same three records and three columns, with no CSV header.
- The in-memory SQLite design is retained; this lab does not add persistence.
- Salary rules support numeric literals, parentheses, `+`, `-`, `*`, `/` and
  unary signs. Arbitrary Python expressions, calls, names, booleans, containers,
  attributes, exponentiation and other operators are deliberately rejected.
  Expressions are limited to 128 characters; every intermediate result must be
  finite and have magnitude at most `10**12`. Invalid input raises `ValueError`.
  Negative arithmetic results are allowed and naturally produce no matches for
  positive salaries, consistent with the original numeric comparison.
- Public helper names are now snake_case; all internal callers were updated.
- Database errors propagate instead of being hidden. Connection transaction
  contexts commit on success and roll back on failure. The script entry point
  closes the database in `finally`.
- CSV uses UTF-8, `newline=""` and `csv.writer` for correct quoting of commas,
  quotation marks and embedded newlines. The CSV is data export, not a hardened
  spreadsheet-formula export; do not treat a clean Bandit scan as a guarantee
  about every downstream CSV consumer.

## Three fixing commits

1. `fix(lab5): resolve Bandit SQL injection, eval and swallowed errors`
2. `fix(lab5): resolve Pylint correctness and maintainability findings`
3. `style(lab5): resolve Flake8 formatting and add verified submission`

The Lab 1 files are preserved, and the assigned program is integrated as the
`Lab5/` directory. Source provenance is recorded above; this is a directory-level
integration, not a merge of the upstream repository's unrelated Git history.
Use `git log -3 --oneline` to inspect the three fixing commits.
