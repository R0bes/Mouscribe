#!/usr/bin/env python3
"""Test runner script for Mauscribe."""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run tests with coverage and generate reports."""
    print("🧪 Mauscribe Test Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: 'src' directory not found!")
        print("Please run this script from the project root.")
        sys.exit(1)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)
    
    # Run tests with coverage
    print("\n🔍 Running tests with coverage...")
    test_cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-fail-under=70",
        "-v"
    ]
    
    try:
        result = subprocess.run(test_cmd, check=False)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("⚠️  Some tests failed")
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
    
    # Show coverage summary
    print("\n📊 Coverage Summary:")
    try:
        subprocess.run([sys.executable, "-m", "coverage", "report"], check=False)
    except Exception:
        print("Could not generate coverage report")
    
    # Open coverage HTML in browser (optional)
    coverage_html = Path("coverage_html/index.html")
    if coverage_html.exists():
        print(f"\n🌐 Coverage report available at: {coverage_html.absolute()}")
        try:
            import webbrowser
            webbrowser.open(f"file://{coverage_html.absolute()}")
        except ImportError:
            pass
    
    print("\n" + "=" * 50)
    print("🎉 Test run completed!")

if __name__ == "__main__":
    main()
