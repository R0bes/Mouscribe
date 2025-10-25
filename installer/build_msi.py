#!/usr/bin/env python3
"""
MSI Build Script for Mauscribe

This script automates the creation of MSI installers using WiX Toolset.
It downloads WiX if not present, compiles the .wxs file, and creates the MSI.

Usage:
    python installer/build_msi.py [--version VERSION] [--output-dir DIR] [--verbose]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional


class MSIBuilder:
    """Builds MSI installers using WiX Toolset."""

    def __init__(self, version: str = "1.0.0", output_dir: str = "dist", verbose: bool = False):
        self.version = version
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.wix_dir = Path("tools/wix")
        self.features_file = Path("installer/features.json")
        self.wxs_file = Path("installer/mauscribe.wxs")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            # Replace Unicode characters for Windows compatibility
            safe_message = message.replace("✅", "[OK]").replace("❌", "[FAIL]").replace("⚠️", "[WARN]")
            print(f"[{level}] {safe_message}")

    def download_wix_toolset(self) -> bool:
        """Download and extract WiX Toolset if not present."""
        wix_exe = self.wix_dir / "bin" / "candle.exe"

        if wix_exe.exists():
            self.log("WiX Toolset already present")
            return True

        self.log("Downloading WiX Toolset...")

        # WiX Toolset download URL (latest stable)
        wix_url = "https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"

        try:
            # Create tools directory
            self.wix_dir.mkdir(parents=True, exist_ok=True)

            # Download WiX
            zip_path = self.wix_dir / "wix.zip"
            self.log(f"Downloading from {wix_url}")

            urllib.request.urlretrieve(wix_url, zip_path)

            # Extract WiX
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.wix_dir)

            # Clean up zip file
            zip_path.unlink()

            # Verify installation
            if wix_exe.exists():
                self.log("WiX Toolset downloaded successfully")
                return True
            else:
                self.log("WiX Toolset download failed - executable not found", "ERROR")
                return False

        except Exception as e:
            self.log(f"Failed to download WiX Toolset: {e}", "ERROR")
            return False

    def load_features(self) -> dict:
        """Load feature configuration from JSON file."""
        try:
            with open(self.features_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Failed to load features: {e}", "ERROR")
            return {}

    def update_wxs_version(self) -> bool:
        """Update version in .wxs file."""
        try:
            # Read current .wxs file
            with open(self.wxs_file, encoding="utf-8") as f:
                content = f.read()

            # Replace version placeholder
            updated_content = content.replace('Version="1.0.0"', f'Version="{self.version}"')

            # Write updated content
            with open(self.wxs_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

            self.log(f"Updated .wxs file with version {self.version}")
            return True

        except Exception as e:
            self.log(f"Failed to update .wxs version: {e}", "ERROR")
            return False

    def validate_files(self) -> bool:
        """Validate that all required files exist."""
        self.log("Validating required files...")

        required_files = [
            "dist/Mauscribe.exe",
            "dist/settings.toml",
            "dist/src/ui/icons/icon.ico",
            "dist/src/ui/icons/icon_idle.ico",
            "dist/src/ui/icons/icon_record.ico",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.log(f"Missing required files: {missing_files}", "ERROR")
            return False

        self.log("All required files present")
        return True

    def compile_wxs(self) -> bool:
        """Compile .wxs file to .wixobj using candle.exe."""
        self.log("Compiling .wxs file...")

        candle_exe = self.wix_dir / "bin" / "candle.exe"
        if not candle_exe.exists():
            self.log("candle.exe not found", "ERROR")
            return False

        # Output directory for .wixobj files
        obj_dir = self.output_dir / "installer"
        obj_dir.mkdir(parents=True, exist_ok=True)

        try:
            cmd = [str(candle_exe), str(self.wxs_file), "-out", str(obj_dir / "mauscribe.wixobj"), "-ext", "WixUIExtension"]

            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.log("WXS compilation successful")
                return True
            else:
                self.log(f"WXS compilation failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Failed to compile WXS: {e}", "ERROR")
            return False

    def link_msi(self) -> bool:
        """Link .wixobj files to MSI using light.exe."""
        self.log("Linking MSI...")

        light_exe = self.wix_dir / "bin" / "light.exe"
        if not light_exe.exists():
            self.log("light.exe not found", "ERROR")
            return False

        obj_dir = self.output_dir / "installer"
        wixobj_file = obj_dir / "mauscribe.wixobj"

        if not wixobj_file.exists():
            self.log("WIXOBJ file not found", "ERROR")
            return False

        try:
            msi_file = self.output_dir / f"Mauscribe-{self.version}.msi"

            cmd = [
                str(light_exe),
                str(wixobj_file),
                "-out",
                str(msi_file),
                "-ext",
                "WixUIExtension",
                "-ext",
                "WixUtilExtension",
            ]

            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.log(f"MSI created successfully: {msi_file}")
                return True
            else:
                self.log(f"MSI linking failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Failed to link MSI: {e}", "ERROR")
            return False

    def validate_msi(self) -> bool:
        """Validate the created MSI file."""
        self.log("Validating MSI...")

        msi_file = self.output_dir / f"Mauscribe-{self.version}.msi"

        if not msi_file.exists():
            self.log("MSI file not found", "ERROR")
            return False

        # Check file size
        file_size = msi_file.stat().st_size
        self.log(f"MSI file size: {file_size:,} bytes")

        if file_size < 1024 * 1024:  # Less than 1MB
            self.log("MSI file seems too small", "WARNING")

        # Try to get MSI info using Windows tools
        try:
            # Use Windows MSI tools if available
            result = subprocess.run(["msiinfo", "summary", str(msi_file)], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.log("MSI validation successful")
                return True
            else:
                self.log("MSI validation failed", "WARNING")
                return True  # Don't fail the build for validation issues

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("MSI validation tools not available", "WARNING")
            return True

    def generate_installer_metadata(self) -> bool:
        """Generate metadata about the installer."""
        self.log("Generating installer metadata...")

        msi_file = self.output_dir / f"Mauscribe-{self.version}.msi"

        if not msi_file.exists():
            self.log("MSI file not found for metadata generation", "ERROR")
            return False

        try:
            metadata = {
                "installer": {
                    "file": str(msi_file),
                    "version": self.version,
                    "size_bytes": msi_file.stat().st_size,
                    "created": msi_file.stat().st_mtime,
                    "type": "msi",
                },
                "features": self.load_features(),
                "build_info": {"wix_version": "3.11.2", "build_tool": "build_msi.py", "platform": "windows"},
            }

            metadata_file = self.output_dir / f"installer-metadata-{self.version}.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            self.log(f"Installer metadata saved: {metadata_file}")
            return True

        except Exception as e:
            self.log(f"Failed to generate metadata: {e}", "ERROR")
            return False

    def build(self) -> bool:
        """Build the MSI installer."""
        self.log(f"Building MSI installer for version {self.version}")

        steps = [
            ("Download WiX Toolset", self.download_wix_toolset),
            ("Load Features", lambda: bool(self.load_features())),
            ("Update WXS Version", self.update_wxs_version),
            ("Validate Files", self.validate_files),
            ("Compile WXS", self.compile_wxs),
            ("Link MSI", self.link_msi),
            ("Validate MSI", self.validate_msi),
            ("Generate Metadata", self.generate_installer_metadata),
        ]

        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not step_func():
                self.log(f"Step failed: {step_name}", "ERROR")
                return False

        self.log("MSI build completed successfully")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build MSI installer for Mauscribe")
    parser.add_argument("--version", default="1.0.0", help="Version number for the installer (default: 1.0.0)")
    parser.add_argument("--output-dir", default="dist", help="Output directory for MSI file (default: dist)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    builder = MSIBuilder(args.version, args.output_dir, args.verbose)
    success = builder.build()

    if success:
        msi_file = Path(args.output_dir) / f"Mauscribe-{args.version}.msi"
        print(f"[OK] MSI installer created: {msi_file}")
        sys.exit(0)
    else:
        print("[FAIL] MSI build failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
