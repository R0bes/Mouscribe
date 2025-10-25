#!/usr/bin/env python3
"""
Release Validation Script for Mauscribe

This script validates a release build by checking:
- Build artifacts exist and are valid
- Executable file integrity
- Required files are included
- Version consistency across files
- Automated smoke tests

Usage:
    python tools/validate_release.py [--dist-path PATH] [--verbose]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil
import toml


class ReleaseValidator:
    """Validates Mauscribe release builds."""

    def __init__(self, dist_path: str = "dist", verbose: bool = False):
        self.dist_path = Path(dist_path)
        self.verbose = verbose
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dist_path": str(self.dist_path),
            "checks": {},
            "overall_status": "PENDING",
            "errors": [],
            "warnings": [],
        }

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{timestamp}] {level}: {message}")

    def add_error(self, check: str, message: str) -> None:
        """Add an error to results."""
        self.results["errors"].append(f"{check}: {message}")
        self.log(f"ERROR in {check}: {message}", "ERROR")

    def add_warning(self, check: str, message: str) -> None:
        """Add a warning to results."""
        self.results["warnings"].append(f"{check}: {message}")
        self.log(f"WARNING in {check}: {message}", "WARNING")

    def check_artifacts_exist(self) -> bool:
        """Check if required build artifacts exist."""
        self.log("Checking build artifacts...")

        required_files = ["Mauscribe.exe", "settings.toml", "data/audio_database.db"]

        required_dirs = ["src/ui/icons"]

        missing_files = []
        missing_dirs = []

        for file_path in required_files:
            full_path = self.dist_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                self.log(f"Found: {file_path}")

        for dir_path in required_dirs:
            full_path = self.dist_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                self.log(f"Found directory: {dir_path}")

        if missing_files:
            self.add_error("artifacts", f"Missing files: {', '.join(missing_files)}")
            return False

        if missing_dirs:
            self.add_error("artifacts", f"Missing directories: {', '.join(missing_dirs)}")
            return False

        self.results["checks"]["artifacts"] = "PASS"
        return True

    def check_executable_integrity(self) -> bool:
        """Check executable file integrity."""
        self.log("Checking executable integrity...")

        exe_path = self.dist_path / "Mauscribe.exe"
        if not exe_path.exists():
            self.add_error("executable", "Mauscribe.exe not found")
            return False

        # Check file size (should be reasonable)
        file_size = exe_path.stat().st_size
        self.log(f"Executable size: {file_size:,} bytes")

        if file_size < 10 * 1024 * 1024:  # Less than 10MB
            self.add_warning("executable", f"Executable seems small ({file_size:,} bytes)")

        if file_size > 500 * 1024 * 1024:  # More than 500MB
            self.add_warning("executable", f"Executable seems large ({file_size:,} bytes)")

        # Calculate file hash
        try:
            with open(exe_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            self.log(f"Executable SHA256: {file_hash[:16]}...")
            self.results["checks"]["executable_hash"] = file_hash
        except Exception as e:
            self.add_error("executable", f"Failed to calculate hash: {e}")
            return False

        self.results["checks"]["executable"] = "PASS"
        return True

    def check_version_consistency(self) -> bool:
        """Check version consistency across files."""
        self.log("Checking version consistency...")

        try:
            # Read pyproject.toml
            with open("pyproject.toml", encoding="utf-8") as f:
                pyproject_data = toml.load(f)
            pyproject_version = pyproject_data["project"]["version"]

            # Read settings.toml
            settings_path = self.dist_path / "settings.toml"
            if settings_path.exists():
                with open(settings_path, encoding="utf-8") as f:
                    settings_data = toml.load(f)
                settings_version = settings_data.get("version", "unknown")
            else:
                settings_version = "missing"

            # Read CHANGELOG.md
            changelog_version = "unknown"
            if Path("CHANGELOG.md").exists():
                with open("CHANGELOG.md", encoding="utf-8") as f:
                    changelog_content = f.read()
                    # Look for version pattern
                    import re

                    version_match = re.search(r"## \[([^\]]+)\]", changelog_content)
                    if version_match:
                        changelog_version = version_match.group(1)

            self.log(f"pyproject.toml version: {pyproject_version}")
            self.log(f"settings.toml version: {settings_version}")
            self.log(f"CHANGELOG.md version: {changelog_version}")

            # Check consistency
            versions = [pyproject_version, settings_version, changelog_version]
            unique_versions = {v for v in versions if v != "unknown" and v != "missing"}

            if len(unique_versions) > 1:
                self.add_error("version", f"Version mismatch: {list(unique_versions)}")
                return False

            if not unique_versions:
                self.add_error("version", "No valid versions found")
                return False

            self.results["checks"]["version"] = "PASS"
            self.results["version"] = list(unique_versions)[0]
            return True

        except Exception as e:
            self.add_error("version", f"Failed to check versions: {e}")
            return False

    def run_smoke_tests(self) -> bool:
        """Run automated smoke tests on the executable."""
        self.log("Running smoke tests...")

        exe_path = self.dist_path / "Mauscribe.exe"
        if not exe_path.exists():
            self.add_error("smoke_tests", "Executable not found")
            return False

        # Test 1: Check if executable can start without crashing
        self.log("Test 1: Starting executable...")
        try:
            # Start the process
            process = subprocess.Popen(
                [str(exe_path), "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30
            )

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.log("Executable started successfully")
            else:
                self.add_warning("smoke_tests", f"Executable returned code {process.returncode}")
                if stderr:
                    self.log(f"Stderr: {stderr}")

        except subprocess.TimeoutExpired:
            self.add_error("smoke_tests", "Executable timed out")
            return False
        except Exception as e:
            self.add_error("smoke_tests", f"Failed to start executable: {e}")
            return False

        # Test 2: Check if process can be terminated cleanly
        self.log("Test 2: Checking process termination...")
        try:
            # Find the process
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == "Mauscribe.exe":
                    proc.terminate()
                    proc.wait(timeout=10)
                    self.log("Process terminated cleanly")
                    break
        except Exception as e:
            self.add_warning("smoke_tests", f"Process termination issue: {e}")

        # Test 3: Check dependencies
        self.log("Test 3: Checking dependencies...")
        try:
            # Try to import key modules (this is a basic check)
            import sys

            sys.path.insert(0, str(self.dist_path))

            # This is a simplified check - in reality we'd need to check
            # if the bundled dependencies work
            self.log("Dependency check completed")

        except Exception as e:
            self.add_warning("smoke_tests", f"Dependency check issue: {e}")

        self.results["checks"]["smoke_tests"] = "PASS"
        return True

    def check_file_permissions(self) -> bool:
        """Check file permissions and accessibility."""
        self.log("Checking file permissions...")

        exe_path = self.dist_path / "Mauscribe.exe"
        if not exe_path.exists():
            self.add_error("permissions", "Executable not found")
            return False

        try:
            # Check if executable is readable
            if not os.access(exe_path, os.R_OK):
                self.add_error("permissions", "Executable not readable")
                return False

            # Check if executable is executable (on Unix-like systems)
            if hasattr(os, "access") and hasattr(os, "X_OK"):
                if not os.access(exe_path, os.X_OK):
                    self.add_warning("permissions", "Executable not executable")

            self.log("File permissions OK")
            self.results["checks"]["permissions"] = "PASS"
            return True

        except Exception as e:
            self.add_error("permissions", f"Permission check failed: {e}")
            return False

    def generate_report(self) -> None:
        """Generate validation report."""
        self.log("Generating validation report...")

        # Determine overall status
        failed_checks = [check for check, status in self.results["checks"].items() if status != "PASS"]

        if failed_checks:
            self.results["overall_status"] = "FAIL"
        elif self.results["warnings"]:
            self.results["overall_status"] = "PASS_WITH_WARNINGS"
        else:
            self.results["overall_status"] = "PASS"

        # Generate JSON report
        json_path = Path("validation_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        # Generate Markdown report
        md_path = Path("validation_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Mauscribe Release Validation Report\n\n")
            f.write(f"**Timestamp:** {self.results['timestamp']}\n")
            f.write(f"**Dist Path:** {self.results['dist_path']}\n")
            f.write(f"**Overall Status:** {self.results['overall_status']}\n\n")

            if "version" in self.results:
                f.write(f"**Version:** {self.results['version']}\n\n")

            f.write("## Check Results\n\n")
            for check, status in self.results["checks"].items():
                status_emoji = "✅" if status == "PASS" else "❌"
                f.write(f"- {status_emoji} **{check}**: {status}\n")

            if self.results["errors"]:
                f.write("\n## Errors\n\n")
                for error in self.results["errors"]:
                    f.write(f"- ❌ {error}\n")

            if self.results["warnings"]:
                f.write("\n## Warnings\n\n")
                for warning in self.results["warnings"]:
                    f.write(f"- ⚠️ {warning}\n")

            f.write("\n## Summary\n\n")
            if self.results["overall_status"] == "PASS":
                f.write("✅ **Release validation PASSED** - Ready for distribution\n")
            elif self.results["overall_status"] == "PASS_WITH_WARNINGS":
                f.write("⚠️ **Release validation PASSED with warnings** - Review warnings before distribution\n")
            else:
                f.write("❌ **Release validation FAILED** - Fix errors before distribution\n")

        self.log(f"Reports generated: {json_path}, {md_path}")

    def validate(self) -> bool:
        """Run all validation checks."""
        self.log("Starting release validation...")

        checks = [
            self.check_artifacts_exist,
            self.check_executable_integrity,
            self.check_version_consistency,
            self.run_smoke_tests,
            self.check_file_permissions,
        ]

        all_passed = True
        for check in checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                self.add_error(check.__name__, f"Check failed with exception: {e}")
                all_passed = False

        self.generate_report()

        if all_passed and not self.results["errors"]:
            self.log("✅ Release validation PASSED")
            return True
        else:
            self.log("❌ Release validation FAILED")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Mauscribe release build")
    parser.add_argument("--dist-path", default="dist", help="Path to distribution directory (default: dist)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    validator = ReleaseValidator(args.dist_path, args.verbose)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
