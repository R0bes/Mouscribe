#!/usr/bin/env python3
"""Development environment setup script for Mauscribe."""
import subprocess
import sys
from pathlib import Path


def main():
    """Set up development environment."""
    print("🚀 Mauscribe Development Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        sys.exit(1)

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Install development dependencies
    print("\n📦 Installing development dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"],
            check=True,
        )
        print("✅ Development dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

    # Install pre-commit hooks
    print("\n🔧 Installing pre-commit hooks...")
    try:
        subprocess.run([sys.executable, "-m", "pre_commit", "install"], check=True)
        print("✅ Pre-commit hooks installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pre-commit hooks: {e}")
        print("You can install them manually with: pre-commit install")

    # Verify setup
    print("\n🔍 Verifying setup...")

    # Check if tests can run
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✅ Pytest: {result.stdout.strip()}")
    except Exception:
        print("❌ Pytest not working")

    # Check if coverage works
    try:
        result = subprocess.run(
            [sys.executable, "-m", "coverage", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✅ Coverage: {result.stdout.strip()}")
    except Exception:
        print("❌ Coverage not working")

    # Check if black works
    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✅ Black: {result.stdout.strip()}")
    except Exception:
        print("❌ Black not working")

    print("\n" + "=" * 50)
    print("🎉 Development environment setup completed!")
    print("\nNext steps:")
    print("1. Run tests: python run_tests.py")
    print("2. Format code: black src/")
    print("3. Check code quality: flake8 src/")
    print("4. Make a commit to test pre-commit hooks")


if __name__ == "__main__":
    main()
