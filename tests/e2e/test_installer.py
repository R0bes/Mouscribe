#!/usr/bin/env python3
"""
End-to-End Installer Tests for Mauscribe

This module contains end-to-end tests that verify the complete installer
workflow from installation to uninstallation.

Usage:
    python -m pytest tests/e2e/test_installer.py -v
"""

import os
import subprocess
import sys
import tempfile
import time
import unittest
import winreg
from pathlib import Path
from unittest.mock import MagicMock, patch

import psutil


class InstallerE2ETests(unittest.TestCase):
    """End-to-end tests for installer functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = tempfile.mkdtemp(prefix="mauscribe_e2e_test_")
        cls.install_dir = Path(cls.test_dir) / "install"
        cls.msi_file = None
        cls.setup_file = None

        # Look for installer files
        dist_dir = Path("dist")
        if dist_dir.exists():
            for file in dist_dir.glob("*.msi"):
                cls.msi_file = file
                break
            for file in dist_dir.glob("*-Setup.exe"):
                cls.setup_file = file
                break

    def setUp(self):
        """Set up for each test."""
        # Clean up any existing installation
        self._cleanup_installation()

    def tearDown(self):
        """Clean up after each test."""
        # Clean up installation
        self._cleanup_installation()

    def _cleanup_installation(self):
        """Clean up any existing installation."""
        try:
            # Kill any running Mauscribe processes
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == "Mauscribe.exe":
                    proc.terminate()
                    proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

        # Clean up registry entries
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Mauscribe")
        except FileNotFoundError:
            pass

        # Clean up files
        if self.install_dir.exists():
            import shutil

            shutil.rmtree(self.install_dir, ignore_errors=True)

    def test_msi_installation_silent(self):
        """Test MSI installation in silent mode."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        self.log("Testing MSI silent installation...")

        try:
            # Install MSI silently
            cmd = ["msiexec", "/i", str(self.msi_file), "/quiet", "/norestart", f"INSTALLDIR={self.install_dir}"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"MSI installation failed: {result.stderr}")

            # Verify files were installed
            self.assertTrue((self.install_dir / "Mauscribe.exe").exists(), "Main executable not found")
            self.assertTrue((self.install_dir / "settings.toml").exists(), "Settings file not found")
            self.assertTrue((self.install_dir / "icons").exists(), "Icons directory not found")

            self.log("MSI installation successful")

        except subprocess.TimeoutExpired:
            self.fail("MSI installation timed out")
        except Exception as e:
            self.fail(f"MSI installation failed: {e}")

    def test_msi_uninstallation_silent(self):
        """Test MSI uninstallation in silent mode."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        # First install
        self.test_msi_installation_silent()

        self.log("Testing MSI silent uninstallation...")

        try:
            # Get product code from MSI
            result = subprocess.run(["msiinfo", "summary", str(self.msi_file)], capture_output=True, text=True)

            if result.returncode != 0:
                self.skipTest("msiinfo not available")

            # Extract product code (simplified)
            product_code = None
            for line in result.stdout.split("\n"):
                if "Product Code" in line:
                    product_code = line.split(":")[1].strip()
                    break

            if not product_code:
                self.skipTest("Could not extract product code")

            # Uninstall MSI silently
            cmd = ["msiexec", "/x", product_code, "/quiet", "/norestart"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check uninstallation result
            self.assertEqual(result.returncode, 0, f"MSI uninstallation failed: {result.stderr}")

            # Verify files were removed
            self.assertFalse((self.install_dir / "Mauscribe.exe").exists(), "Main executable still exists")

            self.log("MSI uninstallation successful")

        except subprocess.TimeoutExpired:
            self.fail("MSI uninstallation timed out")
        except Exception as e:
            self.fail(f"MSI uninstallation failed: {e}")

    def test_inno_setup_installation_silent(self):
        """Test Inno Setup installation in silent mode."""
        if not self.setup_file:
            self.skipTest("Inno Setup file not found")

        self.log("Testing Inno Setup silent installation...")

        try:
            # Install Inno Setup silently
            cmd = [str(self.setup_file), "/SILENT", f"/DIR={self.install_dir}"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"Inno Setup installation failed: {result.stderr}")

            # Verify files were installed
            self.assertTrue((self.install_dir / "Mauscribe.exe").exists(), "Main executable not found")
            self.assertTrue((self.install_dir / "settings.toml").exists(), "Settings file not found")

            self.log("Inno Setup installation successful")

        except subprocess.TimeoutExpired:
            self.fail("Inno Setup installation timed out")
        except Exception as e:
            self.fail(f"Inno Setup installation failed: {e}")

    def test_feature_selection_msi(self):
        """Test MSI feature selection."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        self.log("Testing MSI feature selection...")

        try:
            # Install with specific features
            cmd = [
                "msiexec",
                "/i",
                str(self.msi_file),
                "/quiet",
                "/norestart",
                f"INSTALLDIR={self.install_dir}",
                "ADDLOCAL=CoreFeature,AudioDatabaseFeature,UIIconsFeature",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"MSI feature installation failed: {result.stderr}")

            # Verify core files
            self.assertTrue((self.install_dir / "Mauscribe.exe").exists(), "Main executable not found")

            # Verify audio database feature
            self.assertTrue((self.install_dir / "data").exists(), "Data directory not found")

            # Verify UI icons feature
            self.assertTrue((self.install_dir / "ui_icons").exists(), "UI icons directory not found")

            self.log("MSI feature selection successful")

        except subprocess.TimeoutExpired:
            self.fail("MSI feature installation timed out")
        except Exception as e:
            self.fail(f"MSI feature installation failed: {e}")

    def test_registry_entries(self):
        """Test that registry entries are created correctly."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        # Install first
        self.test_msi_installation_silent()

        self.log("Testing registry entries...")

        try:
            # Check main registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Mauscribe")

            # Check version
            version, _ = winreg.QueryValueEx(key, "Version")
            self.assertIsNotNone(version, "Version not found in registry")

            # Check install path
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            self.assertEqual(install_path, str(self.install_dir), "Install path mismatch")

            winreg.CloseKey(key)

            self.log("Registry entries verified")

        except FileNotFoundError:
            self.fail("Registry entries not created")
        except Exception as e:
            self.fail(f"Registry verification failed: {e}")

    def test_autostart_feature(self):
        """Test autostart feature installation."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        self.log("Testing autostart feature...")

        try:
            # Install with autostart feature
            cmd = [
                "msiexec",
                "/i",
                str(self.msi_file),
                "/quiet",
                "/norestart",
                f"INSTALLDIR={self.install_dir}",
                "ADDLOCAL=CoreFeature,AutostartFeature",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"Autostart installation failed: {result.stderr}")

            # Check autostart registry entry
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
                value, _ = winreg.QueryValueEx(key, "Mauscribe")
                self.assertIn("Mauscribe.exe", value, "Autostart entry not found")
                winreg.CloseKey(key)
            except FileNotFoundError:
                self.fail("Autostart registry entry not created")

            self.log("Autostart feature verified")

        except subprocess.TimeoutExpired:
            self.fail("Autostart installation timed out")
        except Exception as e:
            self.fail(f"Autostart installation failed: {e}")

    def test_shortcuts_creation(self):
        """Test that shortcuts are created correctly."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        self.log("Testing shortcuts creation...")

        try:
            # Install with shortcuts feature
            cmd = [
                "msiexec",
                "/i",
                str(self.msi_file),
                "/quiet",
                "/norestart",
                f"INSTALLDIR={self.install_dir}",
                "ADDLOCAL=CoreFeature,DesktopShortcutsFeature",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"Shortcuts installation failed: {result.stderr}")

            # Check start menu shortcut
            start_menu_path = (
                Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Mauscribe"
            )
            self.assertTrue(start_menu_path.exists(), "Start menu shortcut not found")

            self.log("Shortcuts creation verified")

        except subprocess.TimeoutExpired:
            self.fail("Shortcuts installation timed out")
        except Exception as e:
            self.fail(f"Shortcuts installation failed: {e}")

    def test_post_install_script(self):
        """Test post-installation script execution."""
        if not self.msi_file:
            self.skipTest("MSI file not found")

        self.log("Testing post-install script...")

        try:
            # Install with post-install script
            cmd = [
                "msiexec",
                "/i",
                str(self.msi_file),
                "/quiet",
                "/norestart",
                f"INSTALLDIR={self.install_dir}",
                "ADDLOCAL=CoreFeature",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Check installation result
            self.assertEqual(result.returncode, 0, f"Post-install installation failed: {result.stderr}")

            # Check if post-install script was executed
            # This would typically create AppData directory or update settings
            appdata_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Mauscribe"
            if appdata_dir.exists():
                self.log("Post-install script executed (AppData created)")
            else:
                self.log("Post-install script may not have executed")

        except subprocess.TimeoutExpired:
            self.fail("Post-install installation timed out")
        except Exception as e:
            self.fail(f"Post-install installation failed: {e}")

    def test_installer_metadata(self):
        """Test installer metadata generation."""
        metadata_file = Path("dist") / "installer-metadata-1.0.0.json"

        if not metadata_file.exists():
            self.skipTest("Installer metadata file not found")

        self.log("Testing installer metadata...")

        try:
            import json

            with open(metadata_file, encoding="utf-8") as f:
                metadata = json.load(f)

            # Check required fields
            self.assertIn("installer", metadata, "Installer section not found")
            self.assertIn("features", metadata, "Features section not found")
            self.assertIn("build_info", metadata, "Build info section not found")

            # Check installer info
            installer_info = metadata["installer"]
            self.assertIn("file", installer_info, "Installer file not specified")
            self.assertIn("version", installer_info, "Installer version not specified")
            self.assertIn("size_bytes", installer_info, "Installer size not specified")

            self.log("Installer metadata verified")

        except Exception as e:
            self.fail(f"Installer metadata verification failed: {e}")

    def log(self, message: str) -> None:
        """Log a test message."""
        print(f"[E2E TEST] {message}")


class InstallerPerformanceTests(unittest.TestCase):
    """Performance tests for installer functionality."""

    def test_installation_time(self):
        """Test that installation completes within reasonable time."""
        msi_file = None
        dist_dir = Path("dist")

        if dist_dir.exists():
            for file in dist_dir.glob("*.msi"):
                msi_file = file
                break

        if not msi_file:
            self.skipTest("MSI file not found")

        install_dir = Path(tempfile.mkdtemp(prefix="mauscribe_perf_test_"))

        try:
            start_time = time.time()

            # Install MSI silently
            cmd = ["msiexec", "/i", str(msi_file), "/quiet", "/norestart", f"INSTALLDIR={install_dir}"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            installation_time = time.time() - start_time

            # Should complete within 10 minutes
            self.assertLess(installation_time, 600, f"Installation took too long: {installation_time:.2f}s")

            # Should complete successfully
            self.assertEqual(result.returncode, 0, f"Installation failed: {result.stderr}")

            print(f"Installation completed in {installation_time:.2f} seconds")

        except subprocess.TimeoutExpired:
            self.fail("Installation timed out")
        finally:
            # Cleanup
            import shutil

            if install_dir.exists():
                shutil.rmtree(install_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
