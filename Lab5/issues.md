# Identified Issues and Corrective Actions

**Student:** Debaditya Chakrabarti · **SRN:** PES1UG24CS140 · **Section:** C

Line references under “Original” refer to
`original/recruitment_tracker.py.txt`; “Final” refers to the cleaned program.
Bandit supplies severity and confidence. Pylint and Flake8 do not use the same
high/medium/low security-severity system; their findings are labelled quality,
correctness or style rather than assigned invented severity levels.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| 1. SQL string interpolation — Bandit B608 | Security: **Medium**, confidence Medium | Original 8; Final 16–23 | Applicant fields were interpolated into SQL. Apostrophes could break the statement and input could change query structure. | Use `?` placeholders and pass values separately to `execute`; verify names and fields containing apostrophes. |
| 2. Unrestricted `eval` — Bandit B307; Pylint W0123 | Security: **Medium**, confidence High | Original 14; Final 26–64, 72 | A salary expression was executed as unrestricted Python code. | Parse a bounded expression with `ast.parse`, recursively allow only numeric constants and approved arithmetic operators, and reject all other nodes. Keep the original arithmetic demo working. |
| 3. Silenced broad exception — Bandit B110; Pylint W0718 | Bandit security: **Low**, confidence High; error handling | Original 24–29; Final 80–86 | `except Exception: pass` hid database failures and made unsuccessful updates appear successful. | Remove the catch-and-ignore block; let SQLite errors reach the caller. Use a transaction context so failures roll back. Test propagation and rollback. |
| 4. Inconsistent return — Pylint R1710 | Correctness | Original 12–21; Final 67–77 | The shortlist returned `None` when no applicant qualified, but a list otherwise. | Always return the result list, including an empty list. Test both missing-role and over-budget cases. |
| 5. Unused local — Pylint W0612; Flake8 F841 | Maintainability | Original 15; removed from Final shortlist | `total_seen` was computed but never used. | Remove the dead assignment rather than suppressing the warning. |
| 6. Unspecified encoding — Pylint W1514 | Portability / data integrity | Original 32; Final 91 | CSV output depended on the platform's default text encoding. | Explicitly open the file with `encoding="utf-8"`; verify Unicode export. |
| 7. Unmanaged file handle — Pylint R1732 | Resource management | Original 32–35; Final 89–95 | An exception during export could bypass the manual `close()`. | Use `with open(...)` so the handle closes on success or failure. |
| 8. Nonstandard function names — Pylint C0103 | Maintainability / style | Original 7, 24, 31, 38; Final 16, 80, 89, 98 | Four helper names did not follow snake_case. | Rename to `add_applicant`, `update_status`, `export_report` and `count_by_status`; update all call sites. |
| 9. Missing documentation — Pylint C0114, C0116 | Maintainability | Original 1, 7, 12, 24, 31, 38, 42; Final 1 and each function | The module and functions lacked purpose/behaviour documentation. | Add concise module and function docstrings, including the supported salary-expression grammar. |
| 10. Excessive line length — Pylint C0301; Flake8 E501 | Style / readability | Original 4, 8, 13, 26, 39; Final corresponding SQL and export statements | Long SQL and chained calls exceeded the tools' line-length limits. | Split SQL literals and wrap calls within parentheses; final source meets Flake8's default 79-character limit. |
| 11. Trailing whitespace — Pylint C0303; Flake8 W291 | Style | Original 15; removed | Spaces remained at the end of the unused-variable line. | Remove the assignment and trailing spaces; rescan the entire program. |
| 12. Missing blank line — Flake8 E302 | Style | Original 31; Final 89 | Only one blank line separated top-level functions. | Use two blank lines between top-level definitions. |

## Additional improvements found during review

These are **manual-review improvements**, not additional findings attributed to
an analysis tool:

- Use `csv.writer` instead of manually joining fields, preserving commas,
  quotation marks, Unicode and embedded newlines.
- Guard the demonstration with `if __name__ == "__main__"` so importing the
  module does not add sample applicants, print output or export a report.
- Close the database in the script's `finally` block.

## Verification

All 12 documented groups are resolved in the final scanner reports. Pylint
improved from **4.47/10 to 10.00/10**; Bandit went from **3 to 0 findings**;
Flake8 went from **8 to 0 findings**. Bandit originally reported no high-severity
findings. All **15 regression tests passed**. No rules were disabled and no
inline suppression comments were added.
