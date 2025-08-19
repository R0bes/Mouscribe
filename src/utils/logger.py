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

# Global flag to prevent multiple initializations
_logging_initialized = False


def setup_logging(config=None):
    """Setup logging configuration for Mauscribe.
    
    Args:
        config: Optional Config object for logging settings
    """
    global _logging_initialized
    
    if _logging_initialized:
        return
    
    # Get logging settings from config or use defaults
    if config and hasattr(config, 'logging_enabled') and config.logging_enabled:
        # Parse log levels from config
        console_level_str = config.logging_console_level if hasattr(config, 'logging_console_level') else "INFO"
        file_level_str = config.logging_file_level if hasattr(config, 'logging_file_level') else "DEBUG"
        
        # Convert string levels to logging constants
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        console_level = level_map.get(console_level_str.upper(), logging.INFO)
        file_level = level_map.get(file_level_str.upper(), logging.DEBUG)
        
        # Check if file logging is enabled
        file_enabled = config.logging_file_enabled if hasattr(config, 'logging_file_enabled') else True
        log_filename = config.logging_filename if hasattr(config, 'logging_filename') else "mauscribe.log"
        
        # Check if external log suppression is enabled
        suppress_external = config.logging_suppress_external if hasattr(config, 'logging_suppress_external') else True
    else:
        # Default values if no config or logging disabled
        console_level = logging.INFO
        file_level = logging.DEBUG
        file_enabled = True
        log_filename = "mauscribe.log"
        suppress_external = True
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)-15s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    # Setup file handler only if enabled
    file_handler = None
    if file_enabled:
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)

    # Setup root logger - but don't add handlers to avoid duplication
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Only add handlers if they don't exist
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        if file_handler:
            root_logger.addHandler(file_handler)

    # Suppress verbose logging from external libraries if enabled
    if suppress_external:
        logging.getLogger("comtypes").setLevel(logging.WARNING)
        logging.getLogger("pycaw").setLevel(logging.WARNING)
        logging.getLogger("pynput").setLevel(logging.WARNING)
        logging.getLogger("faster_whisper").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
    
    _logging_initialized = True


class MauscribeLogger:
    """Custom logger for Mauscribe with optional emoji support."""

    def __init__(self, name: str, config=None):
        """Initialize the Mauscribe logger.

        Args:
            name: Logger name (usually __name__)
            config: Optional Config object for emoji settings
        """
        self.logger = logging.getLogger(name)
        
        # Get emoji mode from config or use default
        if config and hasattr(config, 'logging_emoji_enabled'):
            self._emoji_mode = config.logging_emoji_enabled
        else:
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


def get_logger(name: str, config=None) -> MauscribeLogger:
    """Get a MauscribeLogger instance for the given name.

    Args:
        name: Logger name (usually __name__)
        config: Optional Config object for logger settings

    Returns:
        MauscribeLogger instance
    """
    return MauscribeLogger(name, config)


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
