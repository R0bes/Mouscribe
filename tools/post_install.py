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
            "whisper_models": False,
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

        try:
            # Load features configuration
            with open(self.features_file, encoding="utf-8") as f:
                features_config = json.load(f)

            whisper_feature = features_config.get("features", {}).get("whisper_models", {})
            download_urls = whisper_feature.get("download_urls", {})

            if not download_urls:
                self.log("No Whisper model URLs configured", "WARNING")
                return True

            # Create models directory
            models_dir = self.install_dir / "models"
            models_dir.mkdir(exist_ok=True)

            # Download models
            for model_name, url in download_urls.items():
                model_file = models_dir / f"{model_name}.bin"

                if model_file.exists():
                    self.log(f"Model {model_name} already exists, skipping")
                    continue

                self.log(f"Downloading {model_name} model...")
                self.log(f"URL: {url}")

                try:
                    urllib.request.urlretrieve(url, model_file)
                    self.log(f"Downloaded {model_name} model successfully")
                except Exception as e:
                    self.log(f"Failed to download {model_name} model: {e}", "ERROR")
                    return False

            return True

        except Exception as e:
            self.log(f"Failed to download Whisper models: {e}", "ERROR")
            return False

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
            message += "✓ Audio Database - Store and manage recorded audio files\n"

        if features.get("enhanced_mode", False):
            message += "✓ Enhanced Mode - Advanced transcription features\n"

        if features.get("whisper_models", False):
            message += "✓ Whisper Models - AI-powered transcription models\n"

        if features.get("ui_icons", False):
            message += "✓ UI Icons - Additional interface icons\n"

        if features.get("autostart", False):
            message += "✓ Autostart - Start with Windows\n"

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
        print("✅ Post-installation configuration completed successfully")
        sys.exit(0)
    else:
        print("❌ Post-installation configuration failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
