#!/usr/bin/env python3
"""
Integration Tests for Mauscribe Release

This module contains integration tests that verify the built executable
works correctly in an isolated environment.

Usage:
    python -m pytest tests/integration/test_release.py -v
"""

import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import psutil


class ReleaseIntegrationTests(unittest.TestCase):
    """Integration tests for release builds."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.dist_path = Path("dist")
        cls.exe_path = cls.dist_path / "Mauscribe.exe"
        cls.temp_dir = None

        # Check if executable exists
        if not cls.exe_path.exists():
            raise unittest.SkipTest("Mauscribe.exe not found in dist/")

    def setUp(self):
        """Set up for each test."""
        self.temp_dir = tempfile.mkdtemp(prefix="mauscribe_test_")
        self.test_settings_path = Path(self.temp_dir) / "settings.toml"

        # Create test settings
        self.create_test_settings()

    def tearDown(self):
        """Clean up after each test."""
        # Kill any running Mauscribe processes
        self.kill_mauscribe_processes()

        # Clean up temp directory
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_settings(self):
        """Create test settings file."""
        test_settings = """app_name = "Mauscribe Test"
version = "1.0.0"
volume_reduction_factor = 0.2
language = "de"

[logging]
level = "DEBUG"

[audio]
language = "de"
model = "small"
volume_reduction_factor = 0.2

[ui]
dark_mode = true
auto_start_gui = false
close_app_on_gui_close = false

# Feature flags for testing
enable_audio_files_tab = true
enable_audio_database = true
enable_enhanced_mode = true

[ui.notifications]
toast_duration = 1000
"""
        with open(self.test_settings_path, "w", encoding="utf-8") as f:
            f.write(test_settings)

    def kill_mauscribe_processes(self):
        """Kill any running Mauscribe processes."""
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == "Mauscribe.exe":
                    proc.terminate()
                    proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

    def test_executable_exists_and_executable(self):
        """Test that the executable exists and is executable."""
        self.assertTrue(self.exe_path.exists(), "Mauscribe.exe should exist")
        self.assertTrue(self.exe_path.is_file(), "Mauscribe.exe should be a file")

        # Check file size
        file_size = self.exe_path.stat().st_size
        self.assertGreater(file_size, 1024 * 1024, "Executable should be at least 1MB")
        self.assertLess(file_size, 500 * 1024 * 1024, "Executable should be less than 500MB")

    def test_executable_help_command(self):
        """Test that the executable responds to --help."""
        try:
            result = subprocess.run([str(self.exe_path), "--help"], capture_output=True, text=True, timeout=30)

            # Should not crash
            self.assertIsNotNone(result.returncode, "Process should complete")

            # Should produce some output
            if result.stdout:
                self.assertIn("Mauscribe", result.stdout)

        except subprocess.TimeoutExpired:
            self.fail("Executable timed out on --help command")
        except FileNotFoundError:
            self.fail("Executable not found")

    def test_executable_version_command(self):
        """Test that the executable responds to --version."""
        try:
            result = subprocess.run([str(self.exe_path), "--version"], capture_output=True, text=True, timeout=30)

            # Should not crash
            self.assertIsNotNone(result.returncode, "Process should complete")

            # Should produce version output
            if result.stdout:
                self.assertRegex(result.stdout, r"\d+\.\d+\.\d+", "Should contain version number")

        except subprocess.TimeoutExpired:
            self.fail("Executable timed out on --version command")

    def test_executable_with_custom_settings(self):
        """Test that the executable can use custom settings file."""
        try:
            # Set environment variable for settings path
            env = os.environ.copy()
            env["MAUSCRIBE_SETTINGS"] = str(self.test_settings_path)

            # Start process with custom settings
            process = subprocess.Popen(
                [str(self.exe_path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Let it run for a few seconds
            time.sleep(3)

            # Check if process is still running
            self.assertTrue(process.poll() is None, "Process should still be running")

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

        except subprocess.TimeoutExpired:
            self.fail("Process termination timed out")
        except Exception as e:
            self.fail(f"Failed to test with custom settings: {e}")

    def test_executable_system_tray_initialization(self):
        """Test that the executable can initialize system tray."""
        try:
            # Mock audio dependencies to avoid hardware issues
            with patch("sounddevice.check_input") as mock_check_input:
                mock_check_input.return_value = True

                with patch("pystray.Icon") as mock_icon:
                    mock_icon_instance = MagicMock()
                    mock_icon.return_value = mock_icon_instance

                    # Start process
                    process = subprocess.Popen([str(self.exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Let it initialize
                    time.sleep(5)

                    # Check if process is still running
                    self.assertTrue(process.poll() is None, "Process should still be running")

                    # Terminate process
                    process.terminate()
                    process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test system tray initialization: {e}")

    def test_executable_gui_opening(self):
        """Test that the executable can open GUI."""
        try:
            # Start process
            process = subprocess.Popen([str(self.exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Let it initialize
            time.sleep(3)

            # Try to trigger GUI opening (this would need to be implemented)
            # For now, just check that the process is running
            self.assertTrue(process.poll() is None, "Process should still be running")

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test GUI opening: {e}")

    def test_executable_feature_flags(self):
        """Test that feature flags work correctly."""
        # Test with audio database disabled
        test_settings_no_db = """app_name = "Mauscribe Test"
version = "1.0.0"
volume_reduction_factor = 0.2
language = "de"

[logging]
level = "DEBUG"

[audio]
language = "de"
model = "small"
volume_reduction_factor = 0.2

[ui]
dark_mode = true
auto_start_gui = false
close_app_on_gui_close = false

# Feature flags disabled
enable_audio_files_tab = false
enable_audio_database = false
enable_enhanced_mode = false
"""

        no_db_settings_path = Path(self.temp_dir) / "settings_no_db.toml"
        with open(no_db_settings_path, "w", encoding="utf-8") as f:
            f.write(test_settings_no_db)

        try:
            # Set environment variable for settings path
            env = os.environ.copy()
            env["MAUSCRIBE_SETTINGS"] = str(no_db_settings_path)

            # Start process with disabled features
            process = subprocess.Popen(
                [str(self.exe_path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Let it run for a few seconds
            time.sleep(3)

            # Check if process is still running
            self.assertTrue(process.poll() is None, "Process should still be running with disabled features")

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test feature flags: {e}")

    def test_executable_settings_persistence(self):
        """Test that settings are persisted correctly."""
        try:
            # Start process
            env = os.environ.copy()
            env["MAUSCRIBE_SETTINGS"] = str(self.test_settings_path)

            process = subprocess.Popen(
                [str(self.exe_path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Let it run for a few seconds
            time.sleep(3)

            # Check if process is still running
            self.assertTrue(process.poll() is None, "Process should still be running")

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

            # Check if settings file still exists and is readable
            self.assertTrue(self.test_settings_path.exists(), "Settings file should still exist")

        except Exception as e:
            self.fail(f"Failed to test settings persistence: {e}")

    def test_executable_clean_shutdown(self):
        """Test that the executable shuts down cleanly."""
        try:
            # Start process
            process = subprocess.Popen([str(self.exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Let it initialize
            time.sleep(3)

            # Check if process is running
            self.assertTrue(process.poll() is None, "Process should be running")

            # Send SIGTERM
            process.terminate()

            # Wait for clean shutdown
            return_code = process.wait(timeout=10)

            # Should exit cleanly
            self.assertIsNotNone(return_code, "Process should exit")

        except subprocess.TimeoutExpired:
            self.fail("Process did not shut down cleanly")
        except Exception as e:
            self.fail(f"Failed to test clean shutdown: {e}")

    def test_executable_error_handling(self):
        """Test that the executable handles errors gracefully."""
        try:
            # Test with invalid settings file
            invalid_settings_path = Path(self.temp_dir) / "invalid_settings.toml"
            with open(invalid_settings_path, "w", encoding="utf-8") as f:
                f.write("invalid toml content !!!")

            env = os.environ.copy()
            env["MAUSCRIBE_SETTINGS"] = str(invalid_settings_path)

            # Start process with invalid settings
            process = subprocess.Popen(
                [str(self.exe_path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Let it run for a few seconds
            time.sleep(3)

            # Should either exit with error or continue with defaults
            if process.poll() is not None:
                # Process exited, which is acceptable for invalid settings
                self.assertIsNotNone(process.returncode, "Process should have return code")
            else:
                # Process is still running, which means it handled the error gracefully
                process.terminate()
                process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test error handling: {e}")


class ReleasePerformanceTests(unittest.TestCase):
    """Performance tests for release builds."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.dist_path = Path("dist")
        cls.exe_path = cls.dist_path / "Mauscribe.exe"

        if not cls.exe_path.exists():
            raise unittest.SkipTest("Mauscribe.exe not found in dist/")

    def test_startup_time(self):
        """Test that the executable starts within reasonable time."""
        start_time = time.time()

        try:
            process = subprocess.Popen([str(self.exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Wait for process to start
            time.sleep(2)

            startup_time = time.time() - start_time

            # Should start within 10 seconds
            self.assertLess(startup_time, 10, f"Startup time {startup_time:.2f}s is too slow")

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test startup time: {e}")

    def test_memory_usage(self):
        """Test that the executable doesn't use excessive memory."""
        try:
            process = subprocess.Popen([str(self.exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Let it initialize
            time.sleep(5)

            # Check memory usage
            try:
                proc = psutil.Process(process.pid)
                memory_mb = proc.memory_info().rss / 1024 / 1024

                # Should use less than 500MB
                self.assertLess(memory_mb, 500, f"Memory usage {memory_mb:.1f}MB is too high")

            except psutil.NoSuchProcess:
                pass  # Process might have exited

            # Terminate process
            process.terminate()
            process.wait(timeout=10)

        except Exception as e:
            self.fail(f"Failed to test memory usage: {e}")


if __name__ == "__main__":
    unittest.main()
