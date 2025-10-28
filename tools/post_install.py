#!/usr/bin/env python3
"""
Post-Installation Configuration Script for Mauscribe

This script runs after installation to configure settings based on
the features that were selected during installation.

Usage:
    python tools/post_install.py [--install-dir DIR] [--verbose]
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import winreg
from pathlib import Path
from typing import Dict, List, Optional


class PostInstallConfigurator:
    """Configures Mauscribe after installation."""

    def __init__(self, install_dir: str = ".", verbose: bool = False):
        self.install_dir = Path(install_dir)
        self.verbose = verbose
        self.settings_file = self.install_dir / "settings.toml"
        self.features_file = self.install_dir / "installer" / "features.json"

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def read_installed_features(self) -> dict[str, bool]:
        """Read installed features from registry."""
        features = {
            "audio_database": False,
            "enhanced_mode": False,
            "whisper_tiny": False,
            "whisper_base": False,
            "whisper_small": False,
            "whisper_medium": False,
            "whisper_large": False,
            "ui_icons": False,
            "autostart": False,
        }

        try:
            # Read from registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Mauscribe\Settings")

            for feature_name in features.keys():
                try:
                    value, _ = winreg.QueryValueEx(key, feature_name)
                    features[feature_name] = bool(value)
                except FileNotFoundError:
                    pass  # Feature not installed

            winreg.CloseKey(key)

        except FileNotFoundError:
            self.log("Registry key not found - using defaults", "WARNING")

        return features

    def update_settings_file(self, features: dict[str, bool]) -> bool:
        """Update settings.toml based on installed features."""
        self.log("Updating settings file...")

        if not self.settings_file.exists():
            self.log("Settings file not found", "ERROR")
            return False

        try:
            # Read current settings
            with open(self.settings_file, encoding="utf-8") as f:
                content = f.read()

            # Update feature flags
            updates = {
                "enable_audio_files_tab": features["audio_database"],
                "enable_audio_database": features["audio_database"],
                "enable_enhanced_mode": features["enhanced_mode"],
                "auto_start_gui": features["autostart"],
            }

            # Apply updates
            for key, value in updates.items():
                # Find and replace the setting
                import re

                pattern = rf"^{key}\s*=\s*.*$"
                replacement = f"{key} = {str(value).lower()}"

                if re.search(pattern, content, re.MULTILINE):
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    # Add the setting if it doesn't exist
                    content += f"\n{key} = {str(value).lower()}\n"

            # Write updated settings
            with open(self.settings_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.log("Settings file updated successfully")
            return True

        except Exception as e:
            self.log(f"Failed to update settings file: {e}", "ERROR")
            return False

    def download_whisper_models(self) -> bool:
        """Download Whisper models if requested."""
        self.log("Checking for Whisper model downloads...")

        # Read selected features
        features = self.read_installed_features()

        # Check if any whisper models are selected
        selected_models = [name for name, selected in features.items() if name.startswith("whisper_") and selected]

        if not selected_models:
            self.log("No Whisper models selected for download", "WARNING")
            return True

        try:
            # Load features configuration
            features_config = self._load_features_config()
            if not features_config:
                return False

            whisper_feature = features_config.get("features", {}).get("whisper_models", {})
            download_urls = whisper_feature.get("download_urls", {})
            sizes_mb = whisper_feature.get("sizes_mb", {})

            if not download_urls:
                self.log("No Whisper model URLs configured", "WARNING")
                return True

            # Create models directory in AppData
            appdata_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Mauscribe"
            models_dir = appdata_dir / "models"
            models_dir.mkdir(parents=True, exist_ok=True)

            # Download selected models
            for model_name in selected_models:
                model_id = model_name.replace("whisper_", "")
                url = download_urls.get(model_id)
                size_mb = sizes_mb.get(model_id, 0)

                if not url:
                    self.log(f"No URL configured for model: {model_id}", "WARNING")
                    continue

                model_file = models_dir / f"{model_id}.bin"

                if model_file.exists():
                    self.log(f"Model {model_id} already exists, skipping")
                    continue

                self.log(f"Downloading {model_id} model ({size_mb} MB)...")

                try:
                    # Download with progress
                    self._download_with_progress(url, model_file, model_id, size_mb)
                    self.log(f"Downloaded {model_id} model successfully")
                except Exception as e:
                    self.log(f"Failed to download {model_id} model: {e}", "ERROR")
                    return False

            return True

        except Exception as e:
            self.log(f"Failed to download Whisper models: {e}", "ERROR")
            return False

    def _load_features_config(self) -> Optional[dict]:
        """Load features.json configuration file."""
        # Try multiple possible locations
        possible_paths = [
            self.install_dir / "installer" / "features.json",
            Path("installer") / "features.json",
            Path(__file__).parent.parent / "installer" / "features.json",
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    self.log(f"Failed to load features config from {path}: {e}", "WARNING")

        self.log("Features config file not found", "ERROR")
        return None

    def _download_with_progress(self, url: str, dest_file: Path, model_name: str, size_mb: int) -> None:
        """Download a file with progress indication."""

        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded_mb = (block_num * block_size) / (1024 * 1024)
                percent = min(100, (block_num * block_size * 100) / total_size)
                print(f"\rDownloading {model_name}: {downloaded_mb:.1f} MB / {size_mb} MB ({percent:.1f}%)", end="")

        print(f"\nStarting download of {model_name} ({size_mb} MB)...")
        urllib.request.urlretrieve(url, dest_file, report_progress)
        print()  # New line after progress

    def create_appdata_directory(self) -> bool:
        """Create AppData directory structure."""
        self.log("Creating AppData directory...")

        try:
            appdata_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Mauscribe"
            appdata_dir.mkdir(exist_ok=True)

            # Create subdirectories
            (appdata_dir / "logs").mkdir(exist_ok=True)
            (appdata_dir / "cache").mkdir(exist_ok=True)
            (appdata_dir / "temp").mkdir(exist_ok=True)

            self.log(f"AppData directory created: {appdata_dir}")
            return True

        except Exception as e:
            self.log(f"Failed to create AppData directory: {e}", "ERROR")
            return False

    def setup_autostart(self) -> bool:
        """Set up autostart if requested."""
        self.log("Setting up autostart...")

        try:
            # Check if autostart is enabled
            features = self.read_installed_features()
            if not features.get("autostart", False):
                self.log("Autostart not enabled, skipping")
                return True

            # Registry key is already set by the installer
            self.log("Autostart configured in registry")
            return True

        except Exception as e:
            self.log(f"Failed to setup autostart: {e}", "ERROR")
            return False

    def create_welcome_message(self, features: dict[str, bool]) -> str:
        """Create welcome message for installed features."""
        message = "Mauscribe Installation Complete!\n\n"
        message += "Installed features:\n"

        if features.get("audio_database", False):
            message += "[OK] Audio Database - Store and manage recorded audio files\n"

        if features.get("enhanced_mode", False):
            message += "[OK] Enhanced Mode - Advanced transcription features\n"

        # Whisper models
        model_names = {
            "whisper_tiny": "Tiny (39 MB) - Fastest",
            "whisper_base": "Base (74 MB) - Balanced",
            "whisper_small": "Small (244 MB) - Good",
            "whisper_medium": "Medium (769 MB) - Very Good",
            "whisper_large": "Large (1550 MB) - Best Quality",
        }

        for model_key, model_desc in model_names.items():
            if features.get(model_key, False):
                message += f"[OK] Whisper Model: {model_desc}\n"

        if features.get("ui_icons", False):
            message += "[OK] UI Icons - Additional interface icons\n"

        if features.get("autostart", False):
            message += "[OK] Autostart - Start with Windows\n"

        message += "\nYou can now start using Mauscribe!"
        return message

    def show_welcome_screen(self, features: dict[str, bool]) -> None:
        """Show welcome screen with feature summary."""
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()  # Hide the main window

            message = self.create_welcome_message(features)
            messagebox.showinfo("Mauscribe Installation", message)

            root.destroy()

        except ImportError:
            # Fallback to console output
            print("\n" + "=" * 50)
            print(self.create_welcome_message(features))
            print("=" * 50 + "\n")
        except Exception as e:
            self.log(f"Failed to show welcome screen: {e}", "WARNING")

    def configure(self) -> bool:
        """Run post-installation configuration."""
        self.log("Starting post-installation configuration...")

        # Read installed features
        features = self.read_installed_features()
        self.log(f"Installed features: {features}")

        # Run configuration steps
        steps = [
            ("Update Settings File", lambda: self.update_settings_file(features)),
            ("Create AppData Directory", self.create_appdata_directory),
            ("Setup Autostart", self.setup_autostart),
            ("Download Whisper Models", self.download_whisper_models),
        ]

        for step_name, step_func in steps:
            self.log(f"Step: {step_name}")
            if not step_func():
                self.log(f"Step failed: {step_name}", "ERROR")
                return False

        # Show welcome screen
        self.show_welcome_screen(features)

        self.log("Post-installation configuration completed successfully")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Post-installation configuration for Mauscribe")
    parser.add_argument("--install-dir", default=".", help="Installation directory (default: current directory)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    configurator = PostInstallConfigurator(args.install_dir, args.verbose)
    success = configurator.configure()

    if success:
        print("[OK] Post-installation configuration completed successfully")
        sys.exit(0)
    else:
        print("[FAIL] Post-installation configuration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
