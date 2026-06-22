param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $Args
)

# Simple CI-friendly test runner for Windows PowerShell
# Usage: .\run-tests.ps1 accounts
& python manage.py test @Args