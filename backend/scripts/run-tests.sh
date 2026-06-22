#!/usr/bin/env bash
set -euo pipefail

# Simple CI-friendly test runner for Unix-like environments
# Usage: ./run-tests.sh [django_test_labels or options]
python manage.py test "$@"
