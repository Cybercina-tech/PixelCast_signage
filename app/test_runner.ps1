# Test runner PowerShell script
# Usage: .\test_runner.ps1 [test_module]

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$env:PIXELCAST_SIGNAGE_INSTALLED = "true"

if ($args.Count -eq 0) {
    python -m pytest tests/ -q
} else {
    python -m pytest "tests/$($args[0])" -q
}
