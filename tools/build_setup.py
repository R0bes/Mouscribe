#!/usr/bin/env python3
"""
Build Setup.exe Script

This script builds the Mauscribe Windows installer (Setup.exe) using Inno Setup.

Usage:
    python tools/build_setup.py [--verbose]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_inno_setup_compiler() -> Path:
    """
    Find Inno Setup Compiler installation.

    Returns:
        Path to ISCC.exe
    """
    # Common installation paths
    common_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(os.path.expanduser("~")) / r"AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    ]

    for path in common_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Inno Setup Compiler not found. Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php"
    )


def get_version() -> str:
    """Get version from pyproject.toml."""
    import tomli

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return "1.0.0"

    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)

    return pyproject.get("project", {}).get("version", "1.0.0")


def build_executable() -> bool:
    """Build the Mauscribe executable using PyInstaller."""
    print("[INFO] Building Mauscribe executable...")

    try:
        # Check if spec file exists
        spec_file = Path("mauscribe.spec")
        if not spec_file.exists():
            print("[ERROR] mauscribe.spec not found")
            return False

        # Run PyInstaller
        result = subprocess.run(
            ["pyinstaller", "mauscribe.spec", "--clean", "--noconfirm"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"[ERROR] PyInstaller failed: {result.stderr}")
            return False

        print("[OK] Executable built successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to build executable: {e}")
        return False


def build_setup_exe(verbose: bool = False) -> bool:
    """Build the Setup.exe installer using Inno Setup."""
    print("[INFO] Building Setup.exe installer...")

    try:
        # Find Inno Setup Compiler
        iscc_path = find_inno_setup_compiler()
        print(f"[INFO] Using Inno Setup Compiler: {iscc_path}")

        # Check if script exists
        script_path = Path("installer/mauscribe.iss")
        if not script_path.exists():
            print(f"[ERROR] Inno Setup script not found: {script_path}")
            return False

        # Build version info
        version = get_version()
        print(f"[INFO] Building installer for version {version}")

        # Run Inno Setup Compiler
        cmd = [str(iscc_path), str(script_path)]
        if verbose:
            cmd.append("/O+")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("[ERROR] Inno Setup compilation failed:")
            print(result.stderr)
            return False

        print("[OK] Setup.exe built successfully")

        # Find the output file
        output_file = Path(f"dist/Mauscribe-{version}-Setup.exe")
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"[INFO] Installer created: {output_file} ({size_mb:.1f} MB)")

        return True

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to build Setup.exe: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Mauscribe Setup.exe installer")
    parser.add_argument("--skip-build", action="store_true", help="Skip executable build")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("=" * 60)
    print("Mauscribe Setup.exe Builder")
    print("=" * 60)

    # Step 1: Build executable (unless skipped)
    if not args.skip_build:
        if not build_executable():
            print("[FAIL] Build failed")
            sys.exit(1)
    else:
        print("[INFO] Skipping executable build")

    # Step 2: Build Setup.exe
    if not build_setup_exe(verbose=args.verbose):
        print("[FAIL] Setup.exe build failed")
        sys.exit(1)

    print("=" * 60)
    print("[OK] Build completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
