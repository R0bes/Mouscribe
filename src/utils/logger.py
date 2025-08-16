# src/logger.py - Custom Logger for Mauscribe
"""
Custom logger implementation for Mauscribe with optional emoji support.
Provides a wrapper around Python's standard logging with enhanced emoji functionality.
"""

import logging
import warnings
from typing import Optional

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


# Configure logging
def setup_logging():
    """Setup logging configuration for Mauscribe."""

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)-15s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Setup file handler
    file_handler = logging.FileHandler("mauscribe.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Suppress verbose logging from external libraries
    logging.getLogger("comtypes").setLevel(logging.WARNING)
    logging.getLogger("pycaw").setLevel(logging.WARNING)
    logging.getLogger("pynput").setLevel(logging.WARNING)
    logging.getLogger("faster_whisper").setLevel(logging.WARNING)


class MauscribeLogger:
    """Custom logger for Mauscribe with optional emoji support."""

    def __init__(self, name: str):
        """Initialize the Mauscribe logger.

        Args:
            name: Logger name (usually __name__)
        """
        self.logger = logging.getLogger(name)
        self._emoji_mode = True  # Default to emoji mode

    def set_emoji_mode(self, enabled: bool) -> None:
        """Enable or disable emoji mode.

        Args:
            enabled: True to enable emojis, False to disable
        """
        self._emoji_mode = enabled

    def _format_message(self, emoji: str, message: str) -> str:
        """Format message with optional emoji.

        Args:
            emoji: Emoji to prepend to message
            message: The log message

        Returns:
            Formatted message with or without emoji
        """
        if self._emoji_mode and emoji:
            return f"{emoji} {message}"
        return message

    def debug(self, message: str, emoji: str = "") -> None:
        """Log debug message with optional emoji.

        Args:
            message: Debug message to log
            emoji: Optional emoji to prepend
        """
        self.logger.debug(self._format_message(emoji, message))

    def info(self, message: str, emoji: str = "") -> None:
        """Log info message with optional emoji.

        Args:
            message: Info message to log
            emoji: Optional emoji to prepend
        """
        self.logger.info(self._format_message(emoji, message))

    def warning(self, message: str, emoji: str = "") -> None:
        """Log warning message with optional emoji.

        Args:
            message: Warning message to log
            emoji: Optional emoji to prepend
        """
        self.logger.warning(self._format_message(emoji, message))

    def error(self, message: str, emoji: str = "") -> None:
        """Log error message with optional emoji.

        Args:
            message: Error message to log
            emoji: Optional emoji to prepend
        """
        self.logger.error(self._format_message(emoji, message))

    def critical(self, message: str, emoji: str = "") -> None:
        """Log critical message with optional emoji.

        Args:
            message: Critical message to log
            emoji: Optional emoji to prepend
        """
        self.logger.critical(self._format_message(emoji, message))

    def exception(self, message: str, emoji: str = "") -> None:
        """Log exception message with optional emoji.

        Args:
            message: Exception message to log
            emoji: Optional emoji to prepend
        """
        self.logger.exception(self._format_message(emoji, message))

    def is_enabled_for(self, level: int) -> bool:
        """Check if logger is enabled for the given level.

        Args:
            level: Logging level to check

        Returns:
            True if logger is enabled for the level
        """
        return self.logger.isEnabledFor(level)

    def get_effective_level(self) -> int:
        """Get the effective level of the logger.

        Returns:
            Effective logging level
        """
        return self.logger.getEffectiveLevel()


def get_logger(name: str) -> MauscribeLogger:
    """Get a MauscribeLogger instance for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        MauscribeLogger instance
    """
    return MauscribeLogger(name)


# Convenience function for quick emoji logging
def log_with_emoji(
    level: str, message: str, emoji: str = "", logger_name: Optional[str] = None
) -> None:
    """Quick logging function with emoji support.

    Args:
        level: Log level ('debug', 'info', 'warning', 'error', 'critical')
        message: Message to log
        emoji: Optional emoji to prepend
        logger_name: Optional logger name (uses 'mauscribe' if not specified)
    """
    if logger_name is None:
        logger_name = "mauscribe"

    logger = get_logger(logger_name)

    level_method = getattr(logger, level.lower(), logger.info)
    level_method(message, emoji)
