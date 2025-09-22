# src/utils/logger.py - Simple Logger for Mauscribe
"""
Simple logger implementation for Mauscribe.
Provides console and file logging with clean, minimal configuration.
"""
import logging
import warnings
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ModuleSettings removed - using BaseSettings directly

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


class LoggingSettings(BaseSettings):
    enabled: bool = Field(default=True, description="Enable logging")
    console_level: str = Field(default="INFO", description="Console log level")
    file_level: str = Field(default="DEBUG", description="File log level")
    file_enabled: bool = Field(default=True, description="Enable file logging")
    filename: str = Field(default="mauscribe.log", description="Log filename")
    suppress_external_logs: bool = Field(default=True, description="Suppress external library logs")
    model_config = {"env_prefix": "MAUSCRIBE_LOGGING_"}


# Global flag to prevent multiple initializations
_logging_initialized = False


def setup_logging() -> None:
    """Setup logging configuration for Mauscribe.

    Args:
        config: Optional Config object for logging settings
    """
    global _logging_initialized

    if _logging_initialized:
        return

    settings = LoggingSettings()

    # Get logging settings from config or use defaults
    if settings and hasattr(settings, "logging") and settings.logging.enabled:
        # Parse log levels from config
        console_level_str = settings.logging.console_level
        file_level_str = settings.logging.file_level

        # Convert string levels to logging constants
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        console_level = level_map.get(console_level_str.upper(), logging.INFO)
        file_level = level_map.get(file_level_str.upper(), logging.DEBUG)

        # Check if file logging is enabled
        file_enabled = settings.logging.file_enabled
        log_filename = settings.logging.filename
        suppress_external = settings.logging.suppress_external_logs
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
        # Ensure log directory exists
        log_path = Path(log_filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Only add handlers if they don't exist
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        if file_handler:
            root_logger.addHandler(file_handler)

    # Suppress verbose logging from external libraries if enabled
    if suppress_external:
        external_loggers = ["comtypes", "pycaw", "pynput", "faster_whisper", "urllib3", "PIL", "pystray", "PIL.Image"]
        for logger_name in external_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    _logging_initialized = True


def get_logger(name: str, config=None) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (usually __name__ or class name)
        config: Optional Config object for logger settings

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)


# Convenience function for quick logging
def log_message(level: str, message: str, logger_name: Optional[str] = None) -> None:
    """Quick logging function.

    Args:
        level: Log level ('debug', 'info', 'warning', 'error', 'critical')
        message: Message to log
        logger_name: Optional logger name (uses 'mauscribe' if not specified)
    """
    if logger_name is None:
        logger_name = "mauscribe"

    logger = get_logger(logger_name)
    level_method = getattr(logger, level.lower(), logger.info)
    level_method(message)
