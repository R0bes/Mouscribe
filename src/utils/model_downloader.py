"""
Model Downloader for Whisper Models

This module provides functionality to download and manage Whisper AI models
for offline transcription.
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Callable, Optional, Tuple


class ModelDownloader:
    """Handles downloading and management of Whisper models."""

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize the model downloader.

        Args:
            models_dir: Directory to store models. If None, uses default.
        """
        if models_dir is None:
            # Default to AppData/Mauscribe/models
            appdata = os.getenv("LOCALAPPDATA", "")
            models_dir = Path(appdata) / "Mauscribe" / "models"

        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_features_config(self) -> Optional[dict]:
        """Load the features configuration file."""
        possible_paths = [
            Path("installer") / "features.json",
            Path("..") / "installer" / "features.json",
            Path(__file__).parent.parent.parent / "installer" / "features.json",
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    continue

        return None

    def get_model_info(self, model_id: str) -> Optional[tuple[str, int]]:
        """
        Get download URL and size for a model.

        Args:
            model_id: Model identifier (tiny, base, small, medium, large)

        Returns:
            Tuple of (download_url, size_mb) or None if not found
        """
        config = self.get_features_config()
        if not config:
            return None

        whisper_config = config.get("features", {}).get("whisper_models", {})
        download_urls = whisper_config.get("download_urls", {})
        sizes_mb = whisper_config.get("sizes_mb", {})

        url = download_urls.get(model_id)
        size_mb = sizes_mb.get(model_id, 0)

        if url:
            return (url, size_mb)
        return None

    def is_model_downloaded(self, model_id: str) -> bool:
        """
        Check if a model is already downloaded.

        Args:
            model_id: Model identifier

        Returns:
            True if model exists, False otherwise
        """
        model_file = self.models_dir / f"{model_id}.bin"
        return model_file.exists() and model_file.stat().st_size > 0

    def get_model_path(self, model_id: str) -> Optional[Path]:
        """
        Get the path to a model file.

        Args:
            model_id: Model identifier

        Returns:
            Path to model file or None if not downloaded
        """
        model_file = self.models_dir / f"{model_id}.bin"
        if model_file.exists():
            return model_file
        return None

    def download_model(self, model_id: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Download a Whisper model.

        Args:
            model_id: Model identifier
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            True if download successful, False otherwise
        """
        # Get model info
        model_info = self.get_model_info(model_id)
        if not model_info:
            return False

        url, size_mb = model_info
        model_file = self.models_dir / f"{model_id}.bin"

        # Check if already downloaded
        if model_file.exists() and model_file.stat().st_size > 0:
            return True

        try:

            def report_progress(block_num: int, block_size: int, total_size: int) -> None:
                """Report download progress."""
                if total_size > 0 and progress_callback:
                    downloaded_bytes = block_num * block_size
                    progress_callback(downloaded_bytes, total_size)

            # Download the file
            urllib.request.urlretrieve(url, model_file, report_progress)

            # Verify download
            if model_file.exists() and model_file.stat().st_size > 0:
                return True
            else:
                # Clean up incomplete download
                if model_file.exists():
                    model_file.unlink()
                return False

        except Exception as e:
            # Clean up on error
            if model_file.exists():
                model_file.unlink()
            print(f"Error downloading model {model_id}: {e}")
            return False

    def get_all_model_ids(self) -> list[str]:
        """Get list of all available model IDs."""
        config = self.get_features_config()
        if not config:
            return []

        whisper_config = config.get("features", {}).get("whisper_models", {})
        download_urls = whisper_config.get("download_urls", {})
        return list(download_urls.keys())

    def get_model_descriptions(self) -> dict[str, str]:
        """Get descriptions for all available models."""
        config = self.get_features_config()
        if not config:
            return {}

        whisper_config = config.get("features", {}).get("whisper_models", {})
        descriptions = whisper_config.get("descriptions", {})

        # Build descriptions with sizes if not present
        download_urls = whisper_config.get("download_urls", {})
        sizes_mb = whisper_config.get("sizes_mb", {})

        result = {}
        for model_id in download_urls.keys():
            if model_id in descriptions:
                result[model_id] = descriptions[model_id]
            else:
                size = sizes_mb.get(model_id, 0)
                result[model_id] = f"{model_id.capitalize()} ({size} MB)"

        return result
