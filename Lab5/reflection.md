# Reflection on Static Code Analysis

**Student:** Debaditya Chakrabarti · **SRN:** PES1UG24CS140 · **Section:** C

**Prompt clarification:** The supplied three-page handout and assigned README
refer to reflection questions, but the handout does not enumerate them. The
four prompts below are proposed lab-aligned prompts, not a transcription of
missing questions. These responses should be reviewed and personalised before
submission.

## 1. What did the three tools contribute, and how did their findings differ?

Pylint provided the broadest code-quality review. It identified unrestricted
`eval`, an inconsistent return path, an unused variable, broad exception
handling, missing docstrings, nonstandard function names and file-management
problems. Bandit focused on security-sensitive constructs: interpolated SQL,
`eval` and a catch-and-ignore exception block. Flake8 highlighted line length,
blank-line spacing, trailing whitespace and the unused local. The overlap was
useful corroboration, but the tools were complementary rather than
interchangeable. Their message counts should not be added together as a count
of unique defects because several tools reported the same underlying issue.

## 2. Which issues were prioritised, and what required the most care to fix?

The two medium-severity Bandit findings were prioritised: SQL interpolation
and unrestricted `eval`. SQL placeholders separated query structure from
applicant values, including values containing apostrophes. Replacing `eval`
required more care because the demonstration intentionally uses
`500000 + 150000`. Converting the whole expression directly to an integer would
break that behaviour, while `ast.literal_eval` does not evaluate this addition
expression. A small allowlisted AST evaluator preserved basic arithmetic
without allowing function calls, attributes or arbitrary names. Its input and
numeric bounds also reduce resource-abuse risks. The low-severity swallowed
exception was then removed, followed by correctness and style findings.

## 3. How were the fixes verified, and what are static analysis's limitations?

All three tools were rerun against the cleaned assigned program with their
default checks. Pylint reached 10.00/10, Bandit reported no issues and Flake8
produced an empty report. Fifteen regression tests checked the original demo,
salary filtering and arithmetic, rejected expressions, empty results,
apostrophe-containing data, status counts, observable database failures,
transaction rollback, CSV round trips, export failures and import behaviour.
Static tools cannot establish every business rule or runtime property, and a
high score is not a security proof. For example, correct CSV quoting was found
through review and tested dynamically, not reported by these scans. In-memory
storage remains intentional, and spreadsheet formula interpretation is outside
the fixes made to this data-export program.

## 4. How would static analysis be used in future development?

Static analysis is most effective as a small, repeatable part of development,
not only as a final clean-up exercise. The saved reports establish a baseline,
pinned dependencies make the environment reproducible, and three focused
commits separate security, quality and formatting changes. A future workflow
would run Flake8, Pylint, Bandit and regression tests before committing and in
continuous integration. Findings should be reviewed for relevance and risk,
with meaningful corrections preferred over blanket suppressions. Security and
correctness changes should be supported by regression tests so improving a
score does not silently alter the program's intended behaviour.
