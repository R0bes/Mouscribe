#!/usr/bin/env python3
"""
Mauscribe CLI - Command Line Interface
Provides command-line access to Mauscribe functionality
"""
import argparse
import sys
from pathlib import Path

from ..config import get_config
from ..mouscribe import MauscribeApp
from ..utils import get_logger, setup_logging


def cli() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mauscribe",
        description="Mauscribe - Voice-to-Text Tool mit Push-to-Talk und automatischem Clipboard-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Why the mouse became a voice recognition expert?
It was tired of being clicked around... <;3

Note: This is a Windows-friendly version without Unicode characters.
        """,
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="settings.toml",
        help="Path to configuration file (default: settings.toml)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode with detailed error output",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s 1.0.10",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = get_logger("CLI")

    try:
        # Load configuration using new config system
        config_path = Path(args.config)
        if not config_path.exists():
            logger.info(f"Configuration file not found: {config_path}")
            logger.info("Using default configuration...")

        logger.info(f"Configuration loaded from: {config_path}")

        # Start Mauscribe application
        app = MauscribeApp()
        app.run()

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()
