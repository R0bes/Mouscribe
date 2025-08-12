# Mauscribe PowerShell Build Script
# ===================================

param(
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$CleanOnly,
    [switch]$Help
)

if ($Help) {
    Write-Host "Mauscribe Build Script Options:" -ForegroundColor Cyan
    Write-Host "  -SkipTests    Skip running tests before build" -ForegroundColor Yellow
    Write-Host "  -SkipLint     Skip linting before build" -ForegroundColor Yellow
    Write-Host "  -CleanOnly    Only clean build files, don't build" -ForegroundColor Yellow
    Write-Host "  -Help         Show this help message" -ForegroundColor Yellow
    exit 0
}

Write-Host "Mauscribe PowerShell Build Script" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: pip is not available" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install/update dependencies
Write-Host "`nInstalling/updating dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "`nRunning tests..." -ForegroundColor Yellow
    try {
        python -m pytest tests/ -v
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Tests failed! Build aborted." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✓ Tests passed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to run tests" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "⚠ Skipping tests (--SkipTests specified)" -ForegroundColor Yellow
}

# Run linting (unless skipped)
if (-not $SkipLint) {
    Write-Host "`nRunning linting..." -ForegroundColor Yellow
    try {
        flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Linting failed! Build aborted." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✓ Linting passed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to run linting" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "⚠ Skipping linting (--SkipLint specified)" -ForegroundColor Yellow
}

# Clean build files
Write-Host "`nCleaning build files..." -ForegroundColor Yellow
try {
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
    if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }
    if (Test-Path "*.pyc") { Remove-Item -Force "*.pyc" }
    Write-Host "✓ Build files cleaned successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Some build files could not be cleaned" -ForegroundColor Yellow
}

if ($CleanOnly) {
    Write-Host "`n✓ Clean completed successfully!" -ForegroundColor Green
    Read-Host "Press Enter to exit"
    exit 0
}

# Build executable
Write-Host "`nBuilding executable..." -ForegroundColor Yellow
try {
    python build.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Build failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "✗ Failed to run build script" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if executable was created
$exePath = "dist\mauscribe.exe"
if (Test-Path $exePath) {
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "`n✓ Build completed successfully!" -ForegroundColor Green
    Write-Host "✓ Executable location: $exePath" -ForegroundColor Green
    Write-Host "✓ File size: $([math]::Round($fileSize, 1)) MB" -ForegroundColor Green
} else {
    Write-Host "`n✗ Build failed - executable not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nBuild process completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"
