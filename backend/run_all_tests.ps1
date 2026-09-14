# Test Runner for ResearchMate Backend
# Runs all test files individually to avoid pytest session management issues

$testFiles = @(
    "tests/test_api.py",
    "tests/test_chunker.py",
    "tests/test_comparison.py",
    "tests/test_embedding_service.py",
    "tests/test_gap_analysis.py",
    "tests/test_pdf_extractor.py",
    "tests/test_prompts.py",
    "tests/test_qa_endpoint.py",
    "tests/test_retrieval_service.py",
    "tests/test_section_detector.py"
)

$totalPassed = 0
$totalFailed = 0
$totalSkipped = 0
$failedTests = @()

Write-Host ""
Write-Host "Running All Test Files" -ForegroundColor Cyan
Write-Host "Note: Running tests individually to prevent model initialization conflicts" -ForegroundColor Yellow
Write-Host ""

foreach ($testFile in $testFiles) {
    Write-Host "Running $testFile..." -ForegroundColor Cyan
    
    $output = python -m pytest $testFile -v --tb=short 2>&1 | Out-String
    
    if ($output -match "(\d+) passed") {
        $passed = [int]$matches[1]
        $totalPassed += $passed
        Write-Host "  $passed passed" -ForegroundColor Green
    }
    if ($output -match "(\d+) failed") {
        $failed = [int]$matches[1]
        $totalFailed += $failed
        $failedTests += $testFile
        Write-Host "  $failed FAILED" -ForegroundColor Red
        Write-Host $output
    }
    if ($output -match "(\d+) skipped") {
        $skipped = [int]$matches[1]
        $totalSkipped += $skipped
        Write-Host "  $skipped skipped" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "Total Passed:  $totalPassed" -ForegroundColor Green
Write-Host "Total Failed:  $totalFailed" -ForegroundColor $(if ($totalFailed -gt 0) { "Red" } else { "Green" })
Write-Host "Total Skipped: $totalSkipped" -ForegroundColor Yellow

if ($failedTests.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed test files:" -ForegroundColor Red
    $failedTests | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host ""
    exit 1
} else {
    Write-Host ""
    Write-Host "All tests passed!" -ForegroundColor Green
    Write-Host ""
    exit 0
}
