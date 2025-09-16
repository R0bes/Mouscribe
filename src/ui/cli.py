#!/usr/bin/env python3
"""
Mauscribe CLI - Command Line Interface
Provides command-line access to Mauscribe functionality
"""
import argparse
import sys
from pathlib import Path

from ..mouscribe import MauscribeApp
from ..utils import Settings, get_logger, setup_logging


def cli() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mauscribe",
        description="Mauscribe - Voice-to-Text Tool mit Push-to-Talk und automatischem Clipboard-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Why the mouse became a voice recognition expert?
It was tired of being clicked around... 🐭
        """)
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

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = get_logger("CLI")

    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.info(f"Configuration file not found: {config_path}")
            logger.info("Creating default configuration...")
            Settings.create_default_config(str(config_path))
            logger.info(f"✅ Default configuration created: {config_path}")

        logger.info(f"📁 Configuration loaded from: {config_path}")

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
