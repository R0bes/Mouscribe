# tests/test_updater_simple.py - Simplified Tests for Auto-Updater Feature
"""
Simplified tests for the automatic updater functionality.
"""

import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Füge den src-Ordner zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Importiere das zu testende Modul
from src.updater import (
    CURRENT_VERSION,
    GITHUB_REPO,
    REQUESTS_AVAILABLE,
    UPDATE_CHECK_INTERVAL,
    USER_AGENT,
    AutoUpdater,
    UpdateInfo,
    check_for_updates,
    get_updater,
    stop_updater,
)


class TestUpdateInfoSimple(unittest.TestCase):
    """Simple test cases for UpdateInfo class."""

    def test_init_with_required_parameters(self):
        """Test initialization with required parameters."""
        update_info = UpdateInfo(
            version="2.0.0",
            download_url="https://example.com/update.zip",
            release_notes="Test release notes",
            prerelease=False,
        )

        self.assertEqual(update_info.version, "2.0.0")
        self.assertEqual(update_info.download_url, "https://example.com/update.zip")
        self.assertEqual(update_info.release_notes, "Test release notes")
        self.assertFalse(update_info.prerelease)
        self.assertEqual(update_info.download_size, 0)
        self.assertEqual(update_info.published_at, "")

    def test_str_representation(self):
        """Test string representation."""
        update_info = UpdateInfo("2.0.0", "url", "notes")
        self.assertEqual(str(update_info), "Update 2.0.0 (Stable)")

        prerelease_info = UpdateInfo("2.0.0-beta", "url", "notes", True)
        self.assertEqual(str(prerelease_info), "Update 2.0.0-beta (Pre-release)")

    def test_attribute_assignment(self):
        """Test that attributes can be assigned after initialization."""
        update_info = UpdateInfo("2.0.0", "url", "notes")
        update_info.download_size = 1024
        update_info.published_at = "2024-01-01"
        update_info.download_path = Path("/tmp/test.zip")

        self.assertEqual(update_info.download_size, 1024)
        self.assertEqual(update_info.published_at, "2024-01-01")
        self.assertEqual(update_info.download_path, Path("/tmp/test.zip"))


class TestAutoUpdaterSimple(unittest.TestCase):
    """Simple test cases for AutoUpdater class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock config module
        self.config_patcher = patch("src.updater.config")
        self.mock_config = self.config_patcher.start()
        self.mock_config.auto_update_enabled = True
        self.mock_config.auto_update_check_interval = 3600  # 1 hour

        # Mock requests module
        self.requests_patcher = patch("src.updater.requests")
        self.mock_requests = self.requests_patcher.start()

        # Mock threading
        self.threading_patcher = patch("src.updater.threading")
        self.mock_threading = self.threading_patcher.start()

        # Mock Event class to return real Event instances
        mock_event = MagicMock()
        mock_event.return_value = threading.Event()
        self.mock_threading.Event = mock_event

        # Mock time
        self.time_patcher = patch("src.updater.time")
        self.mock_time = self.time_patcher.start()
        self.mock_time.time.return_value = 1000.0

        # Mock subprocess
        self.subprocess_patcher = patch("src.updater.subprocess")
        self.mock_subprocess = self.subprocess_patcher.start()

        # Mock tempfile
        self.tempfile_patcher = patch("src.updater.tempfile")
        self.mock_tempfile = self.tempfile_patcher.start()

        # Mock zipfile
        self.zipfile_patcher = patch("src.updater.zipfile")
        self.mock_zipfile = self.zipfile_patcher.start()

        # Mock shutil
        self.shutil_patcher = patch("src.updater.shutil")
        self.mock_shutil = self.shutil_patcher.start()

        # Mock sys
        self.sys_patcher = patch("src.updater.sys")
        self.mock_sys = self.sys_patcher.start()
        self.mock_sys.executable = "/path/to/executable.exe"

        # Mock Path
        self.path_patcher = patch("src.updater.Path")
        self.mock_path = self.path_patcher.start()

        # Mock os
        self.os_patcher = patch("src.updater.os")
        self.mock_os = self.os_patcher.start()

        # Create updater instance
        self.updater = AutoUpdater()

        # Mock the stop event methods properly after creating the updater
        self.updater._stop_event.set = MagicMock()

    def tearDown(self):
        """Clean up test fixtures."""
        self.config_patcher.stop()
        self.requests_patcher.stop()
        self.threading_patcher.stop()
        self.time_patcher.stop()
        self.subprocess_patcher.stop()
        self.tempfile_patcher.stop()
        self.zipfile_patcher.stop()
        self.shutil_patcher.stop()
        self.sys_patcher.stop()
        self.path_patcher.stop()
        self.os_patcher.stop()

    def test_init_with_auto_update_enabled(self):
        """Test initialization when auto-update is enabled."""
        self.assertTrue(self.updater._enabled)
        self.assertEqual(self.updater._check_interval, 3600)
        self.assertEqual(self.updater._current_version, CURRENT_VERSION)
        self.assertFalse(self.updater._is_checking)
        self.assertIsInstance(self.updater._stop_event, threading.Event)

    def test_init_with_auto_update_disabled(self):
        """Test initialization when auto-update is disabled."""
        self.mock_config.auto_update_enabled = False

        updater = AutoUpdater()
        self.assertFalse(updater._enabled)

    def test_init_without_requests(self):
        """Test initialization when requests module is not available."""
        with patch("src.updater.REQUESTS_AVAILABLE", False):
            updater = AutoUpdater()
            self.assertFalse(updater._enabled)

    def test_check_for_updates_disabled(self):
        """Test check_for_updates when updater is disabled."""
        self.updater._enabled = False

        result = self.updater.check_for_updates()

        self.assertIsNone(result)

    def test_check_for_updates_too_soon(self):
        """Test check_for_updates when called too soon."""
        self.updater._last_check = 1000.0
        self.mock_time.time.return_value = 1500.0  # 500 seconds later

        result = self.updater.check_for_updates()

        self.assertIsNone(result)

    def test_check_for_updates_force_override(self):
        """Test check_for_updates with force override."""
        self.updater._last_check = 1000.0
        self.mock_time.time.return_value = 1500.0  # 500 seconds later

        with patch.object(self.updater, "_fetch_latest_release") as mock_fetch:
            mock_fetch.return_value = None
            self.updater.check_for_updates(force=True)

            # Should proceed even though it's too soon
            mock_fetch.assert_called_once()

    def test_is_newer_version_semantic_versioning(self):
        """Test version comparison with semantic versioning."""
        # Test newer version
        self.assertTrue(self.updater._is_newer_version("2.0.0"))
        self.assertTrue(self.updater._is_newer_version("1.1.0"))
        self.assertTrue(self.updater._is_newer_version("1.0.1"))

        # Test same version
        self.assertFalse(self.updater._is_newer_version("1.0.0"))

        # Test older version
        self.assertFalse(self.updater._is_newer_version("0.9.9"))
        self.assertFalse(self.updater._is_newer_version("0.1.0"))

    def test_is_newer_version_different_lengths(self):
        """Test version comparison with different version lengths."""
        # Test with different number of components
        # "1.0.0.0" is not newer than "1.0.0" (current version)
        self.assertFalse(self.updater._is_newer_version("1.0.0.0"))
        # "1.0.0.1" is newer than "1.0.0"
        self.assertTrue(self.updater._is_newer_version("1.0.0.1"))
        # "1.0" is not newer than "1.0.0"
        self.assertFalse(self.updater._is_newer_version("1.0"))

    def test_is_newer_version_invalid_format(self):
        """Test version comparison with invalid format."""
        # Test with non-numeric versions
        self.assertTrue(self.updater._is_newer_version("beta"))
        self.assertTrue(self.updater._is_newer_version("alpha"))

        # Test with None
        self.assertFalse(self.updater._is_newer_version(None))

    def test_fetch_latest_release_successful(self):
        """Test successful fetch of latest release."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v2.0.0",
            "body": "Release notes",
            "prerelease": False,
            "assets": [{"name": "mauscribe_2.0.0.zip", "browser_download_url": "https://example.com/update.zip"}],
        }
        mock_response.raise_for_status.return_value = None

        self.mock_requests.get.return_value = mock_response

        result = self.updater._fetch_latest_release()

        self.assertIsNotNone(result)
        self.assertEqual(result.version, "2.0.0")
        self.assertEqual(result.download_url, "https://example.com/update.zip")
        self.assertEqual(result.release_notes, "Release notes")
        self.assertFalse(result.prerelease)

    def test_fetch_latest_release_no_assets(self):
        """Test fetch when no suitable assets are found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"tag_name": "v2.0.0", "body": "Release notes", "prerelease": False, "assets": []}
        mock_response.raise_for_status.return_value = None

        self.mock_requests.get.return_value = mock_response

        result = self.updater._fetch_latest_release()

        self.assertIsNone(result)

    def test_fetch_latest_release_network_error(self):
        """Test fetch with network error."""
        self.mock_requests.get.side_effect = Exception("Network error")

        result = self.updater._fetch_latest_release()

        self.assertIsNone(result)

    def test_get_status(self):
        """Test getting updater status."""
        self.updater._enabled = True
        self.updater._is_checking = False
        self.updater._last_check = 1000.0
        self.updater._check_interval = 3600
        self.updater._current_version = "1.0.0"

        status = self.updater.get_status()

        expected_status = {
            "enabled": True,
            "is_checking": False,
            "last_check": 1000.0,
            "next_check": 4600.0,
            "current_version": "1.0.0",
            "check_interval_hours": 1.0,
        }

        self.assertEqual(status, expected_status)

    def test_stop(self):
        """Test stopping the updater."""
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True
        self.updater._update_thread = mock_thread

        self.updater.stop()

        self.updater._stop_event.set.assert_called_once()
        mock_thread.join.assert_called_once_with(timeout=5)

    def test_stop_no_thread(self):
        """Test stopping updater without thread."""
        self.updater._update_thread = None

        self.updater.stop()

        self.updater._stop_event.set.assert_called_once()


class TestGlobalFunctionsSimple(unittest.TestCase):
    """Simple test cases for global convenience functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the global updater instance
        self.updater_patcher = patch("src.updater._updater_instance")
        self.mock_updater_instance = self.updater_patcher.start()

        # Mock AutoUpdater class
        self.updater_class_patcher = patch("src.updater.AutoUpdater")
        self.mock_updater_class = self.updater_class_patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.updater_patcher.stop()
        self.updater_class_patcher.stop()

    def test_get_updater_first_time(self):
        """Test getting updater for the first time."""
        # Mock the global function directly
        with patch("src.updater._updater_instance", None):
            with patch("src.updater.AutoUpdater") as mock_class:
                result = get_updater()

                mock_class.assert_called_once()
                self.assertEqual(result, mock_class.return_value)

    def test_get_updater_existing_instance(self):
        """Test getting existing updater instance."""
        mock_instance = MagicMock()

        # Mock the global function directly
        with patch("src.updater._updater_instance", mock_instance):
            result = get_updater()

            self.assertEqual(result, mock_instance)

    def test_check_for_updates(self):
        """Test convenience function for update checks."""
        mock_instance = MagicMock()
        mock_instance.check_for_updates.return_value = "update_info"

        # Mock the global function directly
        with patch("src.updater.get_updater") as mock_get_updater:
            mock_get_updater.return_value = mock_instance

            result = check_for_updates(force=True)

            self.assertEqual(result, "update_info")
            # Verify that the method was called
            mock_instance.check_for_updates.assert_called_once()

    def test_stop_updater(self):
        """Test stopping the global updater."""
        mock_instance = MagicMock()

        # Mock the global function directly
        with patch("src.updater._updater_instance", mock_instance):
            stop_updater()

            mock_instance.stop.assert_called_once()

    def test_stop_updater_no_instance(self):
        """Test stopping updater when no instance exists."""
        self.mock_updater_instance = None

        stop_updater()

        # Should not raise any exceptions


class TestUpdaterConstants(unittest.TestCase):
    """Test the constants defined in the updater module."""

    def test_github_repo(self):
        """Test GitHub repository constant."""
        self.assertEqual(GITHUB_REPO, "R0bes/Mauscribe")

    def test_current_version(self):
        """Test current version constant."""
        self.assertEqual(CURRENT_VERSION, "1.0.0")

    def test_update_check_interval(self):
        """Test update check interval constant."""
        self.assertEqual(UPDATE_CHECK_INTERVAL, 24 * 60 * 60)  # 24 hours

    def test_user_agent(self):
        """Test user agent constant."""
        self.assertEqual(USER_AGENT, "Mauscribe-Updater/1.0")

    def test_requests_available(self):
        """Test requests availability constant."""
        self.assertIsInstance(REQUESTS_AVAILABLE, bool)


if __name__ == "__main__":
    unittest.main()
