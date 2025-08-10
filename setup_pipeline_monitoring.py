#!/usr/bin/env python3
"""Setup script for automated pipeline monitoring with git hooks."""

import subprocess
import sys
import os
from pathlib import Path
import platform

def main():
    """Set up automated pipeline monitoring."""
    print("🔧 Setting up Automated Pipeline Monitoring")
    print("=" * 50)
    
    # Check if we're in a git repository
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, check=True)
        git_dir = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository!")
        print("Please run this script from within a git repository.")
        sys.exit(1)
    
    print(f"✅ Git repository found: {git_dir}")
    
    # Get repository root
    try:
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                              capture_output=True, text=True, check=True)
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
            Write-Host "✅ Pipeline monitoring completed successfully" -ForegroundColor Green
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
    set EXIT_CODE=%ERRORLEVEL%
    
    if %EXIT_CODE% EQU 0 (
        echo ✅ Pipeline monitoring completed successfully
    ) else (
        echo ❌ Pipeline monitoring failed or pipelines failed
        echo 💡 Check the output above for details
    )
) else (
    echo ⚠️  Pipeline monitor not found. Skipping monitoring.
)

echo 🏁 Post-push hook completed
"""
        
        # Write both hook files
        with open(hook_script, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        with open(batch_hook, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ Created PowerShell hook: {hook_script}")
        print(f"✅ Created Batch hook: {batch_hook}")
        
    else:
        # Unix/Linux/macOS
        hook_script = hooks_dir / "post-push"
        hook_content = """#!/bin/bash
# Post-push hook to automatically monitor CI/CD pipelines
# This hook runs after every git push

echo "🚀 Post-push hook triggered - Monitoring CI/CD pipelines..."

# Get the current directory (repository root)
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Check if pipeline monitor exists
if [ -f "pipeline_monitor.py" ]; then
    echo "🔍 Starting pipeline monitoring..."
    
    # Run the pipeline monitor
    python pipeline_monitor.py
    
    # Check the exit code
    if [ $? -eq 0 ]; then
        echo "✅ Pipeline monitoring completed successfully"
    else
        echo "❌ Pipeline monitoring failed or pipelines failed"
        echo "💡 Check the output above for details"
    fi
else
    echo "⚠️  Pipeline monitor not found. Skipping monitoring."
fi

echo "🏁 Post-push hook completed"
"""
        
        with open(hook_script, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # Make the hook executable
        os.chmod(hook_script, 0o755)
        print(f"✅ Created executable hook: {hook_script}")
    
    # Create a pre-push hook that ensures the post-push hook runs
    pre_push_hook = hooks_dir / "pre-push"
    pre_push_content = """#!/bin/bash
# Pre-push hook to ensure post-push monitoring is set up

echo "🔍 Pre-push check: Ensuring pipeline monitoring is configured..."

# Check if post-push hook exists
if [ ! -f ".git/hooks/post-push" ] && [ ! -f ".git/hooks/post-push.ps1" ] && [ ! -f ".git/hooks/post-push.bat" ]; then
    echo "⚠️  Warning: No post-push hook found for pipeline monitoring"
    echo "   Run 'python setup_pipeline_monitoring.py' to set up monitoring"
fi

echo "✅ Pre-push check completed"
"""
    
    with open(pre_push_hook, 'w', encoding='utf-8') as f:
        f.write(pre_push_content)
    
    if not is_windows:
        os.chmod(pre_push_hook, 0o755)
    
    print(f"✅ Created pre-push hook: {pre_push_hook}")
    
    # Create a configuration file for the monitoring
    config_file = repo_root / ".pipeline-monitor-config"
    config_content = """# Pipeline Monitor Configuration
# This file contains configuration for automated pipeline monitoring

[monitoring]
enabled = true
max_wait_time = 300
check_interval = 15

[notifications]
show_progress = true
show_job_details = true
open_browser_on_failure = false

[github]
token_source = auto
repo_owner = R0bes
repo_name = Mouscribe
"""
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Created configuration file: {config_file}")
    
    # Test the setup
    print("\n🧪 Testing the setup...")
    
    try:
        # Test if we can import the required modules
        import requests
        print("✅ Required dependencies available")
    except ImportError:
        print("⚠️  Warning: 'requests' module not available")
        print("   Install with: pip install requests")
    
    # Test git hook detection
    hook_files = list(hooks_dir.glob("post-push*"))
    if hook_files:
        print(f"✅ Git hooks created: {', '.join(f.name for f in hook_files)}")
    else:
        print("❌ No git hooks found")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 What happens now:")
    print("1. After every 'git push', the pipeline monitor will automatically run")
    print("2. It will check the status of your CI/CD pipelines")
    print("3. You'll get real-time feedback on pipeline execution")
    print("4. Failed pipelines will show detailed error information")
    
    print("\n🔧 Manual commands:")
    print("  python pipeline_monitor.py          # Monitor pipelines manually")
    print("  python pipeline_monitor.py --open   # Open pipeline status in browser")
    
    print("\n💡 Next steps:")
    print("1. Make a test commit and push to trigger the monitoring")
    print("2. Check that the post-push hook runs automatically")
    print("3. Verify that pipeline status is being monitored")
    
    if is_windows:
        print("\n⚠️  Note: On Windows, you may need to enable PowerShell execution:")
        print("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")

if __name__ == "__main__":
    main()
