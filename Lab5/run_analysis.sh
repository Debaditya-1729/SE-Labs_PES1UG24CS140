#!/usr/bin/env bash
# Run from an activated environment containing requirements-dev.txt.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p reports/after
pylint --persistent=n recruitment_tracker.py > reports/after/pylint_report.txt 2>&1
pylint_status=$?
bandit -r recruitment_tracker.py > reports/after/bandit_report.txt 2>&1
bandit_status=$?
flake8 recruitment_tracker.py > reports/after/flake8_report.txt 2>&1
flake8_status=$?
python -m unittest -v > reports/after/test_report.txt 2>&1
test_status=$?
printf 'pylint=%s\nbandit=%s\nflake8=%s\nunittest=%s\n' \
  "$pylint_status" "$bandit_status" "$flake8_status" "$test_status" \
  > reports/after/exit_statuses.txt
cat reports/after/exit_statuses.txt
if ((pylint_status || bandit_status || flake8_status || test_status)); then
  exit 1
fi
