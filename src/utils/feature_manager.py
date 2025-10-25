# src/utils/feature_manager.py - Feature Flag Management
"""
Feature Manager for optional Mauscribe components.
Allows enabling/disabling features via configuration.
"""

from typing import Any, Optional


class FeatureManager:
    """Manages feature flags for optional components."""

    def __init__(self, config: Optional[Any] = None):
        """Initialize Feature Manager.

        Args:
            config: AppConfig instance for reading feature flags
        """
        self.config = config
        self._features = {
            "audio_files_tab": True,
            "audio_database": True,
            "enhanced_mode": True,
            "mode_selector": True,
        }

    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled.

        Args:
            feature: Feature name to check

        Returns:
            True if feature is enabled, False otherwise
        """
        # Check config first
        if self.config and hasattr(self.config, "ui"):
            config_key = f"enable_{feature}"
            if hasattr(self.config.ui, config_key):
                return getattr(self.config.ui, config_key)

        # Fallback to default
        return self._features.get(feature, False)

    def enable_feature(self, feature: str) -> None:
        """Enable a feature.

        Args:
            feature: Feature name to enable
        """
        self._features[feature] = True

    def disable_feature(self, feature: str) -> None:
        """Disable a feature.

        Args:
            feature: Feature name to disable
        """
        self._features[feature] = False

    def get_enabled_features(self) -> list[str]:
        """Get list of enabled features.

        Returns:
            List of enabled feature names
        """
        return [feature for feature, enabled in self._features.items() if enabled]

    def get_disabled_features(self) -> list[str]:
        """Get list of disabled features.

        Returns:
            List of disabled feature names
        """
        return [feature for feature, enabled in self._features.items() if not enabled]


# Global instance
feature_manager = FeatureManager()
