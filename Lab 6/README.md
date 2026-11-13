# Lab 6: Code and Branch Coverage

**Student:** Debaditya Chakrabarti  
**SRN:** PES1UG24CS140  
**Section:** C  
**Assigned application:** [Library Fines](https://github.com/SETAPESU26/L6_L7_14_library_fines/tree/29fac1ace717b8855298f18d533d61e6e3615517/Lab%206)

The assigned `library_fines.py` and starter `test_library_fines.py` are unchanged copies from source commit `29fac1ace717b8855298f18d533d61e6e3615517`. The two added test files can be run independently. Coverage is limited to the application, not the test files.

## Run

With Python 3, from this directory:

```bash
python -m pip install -r requirements.txt

# Baseline, using the original starter tests
coverage run --source=library_fines -m pytest -q test_library_fines.py
coverage report -m
coverage run --branch --source=library_fines -m pytest -q test_library_fines.py
coverage report -m

# Final line coverage
coverage run --source=library_fines -m pytest -q CodeCoverageTest_140_application.py
coverage report -m

# Final branch coverage
coverage run --branch --source=library_fines -m pytest -q BranchCoverageTest_140_application.py
coverage report -m
coverage json -o coverage-results.json
```

Run each `coverage run` before its corresponding report; each run replaces the previous coverage data. Results below were obtained with Python 3.13, pytest 9.2.0 and coverage.py 7.17.3. The screenshots show the final runs, not the baseline.

## Analysis

Line coverage counts executed statements; branch coverage checks which possible control-flow exits were taken. Neither establishes that all input combinations or paths are correct.

| Suite | Tests passed | Statements covered | Branch exits covered | Coverage.py report |
|---|---:|---:|---:|---:|
| Original starter, line run | 2 | 16/32 (50%) | Not measured | 50% |
| Original starter, branch run | 2 | 16/32 (50%) | 7/22 (32%) | 43% combined |
| Code coverage suite, line run | 4 | 32/32 (100%) | Not measured in this run | 100% |
| Branch coverage suite, branch run | 28 | 32/32 (100%) | 22/22 (100%) | 100% combined |

For a branch run, coverage.py's displayed `Cover` combines statement and branch opportunities; it is not the branch-only percentage. Branch-only counts above are from the JSON report. The line suite also happens to cover all 22 measured branch exits when run with `--branch`; the separate branch suite adds focused boundary and priority cases rather than claiming a further percentage increase.

The starter tests missed error handling for unknown members and negative days, faculty loan rules, overdue fines and their cap, damage charges, borrowing restrictions, and all renewal outcomes. The added tests exercise those paths. The branch suite additionally checks loan deadlines, fine amounts at and above the 200 cap, the borrowing fine and book limits, and renewal limits, overdue boundaries and decision precedence. It also checks that the damage charge is added after the overdue-fine cap.

## Deliverables

- `CodeCoverageTest_140_application.py` — line-coverage tests.
- `BranchCoverageTest_140_application.py` — decision and boundary tests.
- `screenshots/code_coverage.png` and `screenshots/branch_coverage.png` — actual terminal output from successful final runs.
