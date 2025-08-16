#!/usr/bin/env python3
"""Test runner script for Mauscribe."""
import os
import subprocess
import sys


def main():  # noqa: C901
    """Run tests with coverage and generate reports."""
    print("TEST: Mauscribe Test Runner")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("ERROR: 'src' directory not found!")
        print("Please run this script from the project root.")
        sys.exit(1)

    # Install test dependencies if needed
    print("INSTALL: Installing test dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
            check=True,
            capture_output=True,
        )
        print("SUCCESS: Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        sys.exit(1)

    # Run tests with coverage
    print("\nRUNNING: Running tests with coverage...")
    test_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-fail-under=65",
        "-v",
    ]

    try:
        result = subprocess.run(test_cmd, check=False)
        if result.returncode == 0:
            print("SUCCESS: All tests passed!")
        else:
            print("WARNING: Some tests failed")
            print(f"ERROR: Test exit code: {result.returncode}")
        # Return the actual test exit code
        sys.exit(result.returncode)
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        sys.exit(1)

    # Show coverage summary
    print("\nCOVERAGE: Coverage Summary:")
    try:
        subprocess.run([sys.executable, "-m", "coverage", "report"], check=False)
    except Exception:
        print("Could not generate coverage report")

    # Open coverage HTML in browser (optional)
    coverage_html = "coverage_html/index.html"
    if os.path.exists(coverage_html):
        print(
            f"\nBROWSER: Coverage report available at: {os.path.abspath(coverage_html)}"
        )
        try:
            import webbrowser

            webbrowser.open(f"file://{os.path.abspath(coverage_html)}")
        except ImportError:
            pass

    print("\n" + "=" * 50)
    print("COMPLETED: Test run completed!")


if __name__ == "__main__":
    main()
