#!/usr/bin/env python3
"""Setup script for automated pipeline monitoring with git hooks."""

import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    """Set up automated pipeline monitoring."""
    print("🔧 Setting up Automated Pipeline Monitoring")
    print("=" * 50)

    # Check if we're in a git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
        )
        git_dir = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository!")
        print("Please run this script from within a git repository.")
        sys.exit(1)

    print(f"✅ Git repository found: {git_dir}")

    # Get repository root
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("❌ Could not determine repository root")
        sys.exit(1)

    print(f"📁 Repository root: {repo_root}")

    # Check if pipeline_monitor.py exists
    monitor_script = repo_root / "pipeline_monitor.py"
    if not monitor_script.exists():
        print("❌ Error: pipeline_monitor.py not found!")
        print("Please ensure the pipeline monitor script exists.")
        sys.exit(1)

    print("✅ Pipeline monitor script found")

    # Create hooks directory if it doesn't exist
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Determine the appropriate hook script based on platform
    is_windows = platform.system().lower() == "windows"

    if is_windows:
        hook_script = hooks_dir / "post-push.ps1"
        hook_content = """# Post-push hook to automatically monitor CI/CD pipelines
# This hook runs after every git push (PowerShell version for Windows)

Write-Host "🚀 Post-push hook triggered - Monitoring CI/CD pipelines..." -ForegroundColor Green

# Get the current directory (repository root)
$REPO_ROOT = git rev-parse --show-toplevel
Set-Location $REPO_ROOT

# Check if pipeline monitor exists
if (Test-Path "pipeline_monitor.py") {
    Write-Host "🔍 Starting pipeline monitoring..." -ForegroundColor Yellow

    # Run the pipeline monitor
    try {
        python pipeline_monitor.py
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Host "✅ Pipeline monitoring completed" -ForegroundColor Green
        } else {
            Write-Host "❌ Pipeline monitoring failed or pipelines failed" -ForegroundColor Red
            Write-Host "💡 Check the output above for details" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error running pipeline monitor: $_" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Pipeline monitor not found. Skipping monitoring." -ForegroundColor Yellow
}

Write-Host "🏁 Post-push hook completed" -ForegroundColor Green
"""

        # Also create a batch file for compatibility
        batch_hook = hooks_dir / "post-push.bat"
        batch_content = """@echo off
REM Post-push hook to automatically monitor CI/CD pipelines
REM This hook runs after every git push (Batch version for Windows)

echo 🚀 Post-push hook triggered - Monitoring CI/CD pipelines...

REM Get the current directory (repository root)
for /f "delims=" %%i in ('git rev-parse --show-toplevel') do set REPO_ROOT=%%i
cd /d "%REPO_ROOT%"

REM Check if pipeline monitor exists
if exist "pipeline_monitor.py" (
    echo 🔍 Starting pipeline monitoring...
    
    REM Run the pipeline monitor
    python pipeline_monitor.py
    set exitCode=%ERRORLEVEL%
    
    if %exitCode% equ 0 (
        echo ✅ Pipeline monitoring completed
    ) else (
        echo ❌ Pipeline monitoring failed or pipelines failed
        echo 💡 Check the output above for details
    )
) else (
    echo ⚠️  Pipeline monitor not found. Skipping monitoring.
)

echo 🏁 Post-push hook completed
"""

        # Write PowerShell hook
        with open(hook_script, "w", encoding="utf-8") as f:
            f.write(hook_content)

        # Write batch hook
        with open(batch_hook, "w", encoding="utf-8") as f:
            f.write(batch_content)

        print(f"✅ Created PowerShell hook: {hook_script}")
        print(f"✅ Created batch hook: {batch_hook}")

    else:
        # Unix/Linux/macOS hook
        hook_script = hooks_dir / "post-push"
        hook_content = """#!/bin/bash
# Post-push hook to automatically monitor CI/CD pipelines
# This hook runs after every git push

echo "🚀 Post-push hook triggered - Monitoring CI/CD pipelines..."

# Get the current directory (repository root)
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Check if pipeline monitor exists
if [ -f "pipeline_monitor.py" ]; then
    echo "🔍 Starting pipeline monitoring..."
    
    # Run the pipeline monitor
    python3 pipeline_monitor.py
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Pipeline monitoring completed"
    else
        echo "❌ Pipeline monitoring failed or pipelines failed"
        echo "💡 Check the output above for details"
    fi
else
    echo "⚠️  Pipeline monitor not found. Skipping monitoring."
fi

echo "🏁 Post-push hook completed"
"""

        # Write Unix hook
        with open(hook_script, "w", encoding="utf-8") as f:
            f.write(hook_content)

        # Make it executable
        os.chmod(hook_script, 0o755)

        print(f"✅ Created Unix hook: {hook_script}")

    # Create pre-commit hook for local validation
    print("\n🔧 Setting up pre-commit hook for local validation...")
    
    if is_windows:
        pre_commit_script = hooks_dir / "pre-commit.ps1"
        pre_commit_content = """# Pre-commit hook for local validation
# This hook runs before every commit

Write-Host "🔍 Pre-commit hook - Running local validation..." -ForegroundColor Yellow

# Get the current directory (repository root)
$REPO_ROOT = git rev-parse --show-toplevel
Set-Location $REPO_ROOT

# Run local CI checks
try {
    Write-Host "Running linting..." -ForegroundColor Cyan
    python -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --max-line-length=127 --show-source --statistics
    
    Write-Host "Running code formatting check..." -ForegroundColor Cyan
    python -m black --check --line-length=127 src/ tests/
    
    Write-Host "Running import sorting check..." -ForegroundColor Cyan
    python -m isort --check-only src/ tests/
    
    Write-Host "Running tests..." -ForegroundColor Cyan
    python -m pytest tests/ -v --tb=short
    
    Write-Host "✅ All pre-commit checks passed!" -ForegroundColor Green
    exit 0
    
} catch {
    Write-Host "❌ Pre-commit checks failed: $_" -ForegroundColor Red
    Write-Host "💡 Please fix the issues above before committing" -ForegroundColor Yellow
    exit 1
}
"""

        # Write pre-commit hook
        with open(pre_commit_script, "w", encoding="utf-8") as f:
            f.write(pre_commit_content)

        print(f"✅ Created pre-commit hook: {pre_commit_script}")

    else:
        pre_commit_script = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# Pre-commit hook for local validation
# This hook runs before every commit

echo "🔍 Pre-commit hook - Running local validation..."

# Get the current directory (repository root)
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Run local CI checks
echo "Running linting..."
python3 -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --max-line-length=127 --show-source --statistics

echo "Running code formatting check..."
python3 -m black --check --line-length=127 src/ tests/

echo "Running import sorting check..."
python3 -m isort --check-only src/ tests/

echo "Running tests..."
python3 -m pytest tests/ -v --tb=short

echo "✅ All pre-commit checks passed!"
"""

        # Write pre-commit hook
        with open(pre_commit_script, "w", encoding="utf-8") as f:
            f.write(pre_commit_content)

        # Make it executable
        os.chmod(pre_commit_script, 0o755)

        print(f"✅ Created pre-commit hook: {pre_commit_script}")

    print("\n🎯 Pipeline Monitoring Setup Complete!")
    print("=" * 50)
    print("✅ Post-push hook created - Will monitor CI/CD pipelines after push")
    print("✅ Pre-commit hook created - Will validate code before commit")
    print("\n💡 Next steps:")
    print("   1. Make a commit to test the pre-commit hook")
    print("   2. Push to test the post-push hook")
    print("   3. Check GitHub Actions for pipeline status")
    print("\n🔧 Manual monitoring: python pipeline_monitor.py")


if __name__ == "__main__":
    main()
