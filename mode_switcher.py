# mode_switcher.py - Command Line Mode Switcher
"""
Command line tool for switching Mauscribe recording modes.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def switch_mode(mode: str) -> None:
    """Switch Mauscribe recording mode."""
    try:
        from src.config.recording_modes import DEFAULT_ENHANCED_CONFIG, DEFAULT_NORMAL_CONFIG, RecordingMode
        from src.utils.enhanced_database import get_enhanced_database

        # Validate mode
        if mode not in ["normal", "enhanced"]:
            print(f"❌ Invalid mode: {mode}. Use 'normal' or 'enhanced'")
            return

        # Get database instance
        db = get_enhanced_database()

        # End current session if exists
        if db.current_session_id:
            db.end_session()
            print(f"Ended current session: {db.current_session_id}")

        # Start new session with selected mode
        session_id = db.start_session(mode=mode)
        print(f"Started new {mode} session: {session_id}")

        # Update settings file
        update_settings_file(mode)

        print(f"Successfully switched to {mode} mode!")
        print(f"Session ID: {session_id}")

        if mode == "enhanced":
            print("Enhanced mode features:")
            print("   - Audio files saved permanently")
            print("   - Training data collection enabled")
            print("   - Enhanced metadata storage")
        else:
            print("Normal mode features:")
            print("   - Audio files deleted after transcription")
            print("   - Minimal storage usage")
            print("   - Automatic cleanup")

    except Exception as e:
        print(f"Failed to switch mode: {e}")


def update_settings_file(mode: str) -> None:
    """Update settings.toml with new mode."""
    try:
        settings_path = Path("settings.toml")

        if not settings_path.exists():
            print("settings.toml not found, creating default...")
            create_default_settings(mode)
            return

        # Read current settings
        with open(settings_path, encoding="utf-8") as f:
            content = f.read()

        # Update mode setting
        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            if line.strip().startswith("default_mode ="):
                updated_lines.append(f'default_mode = "{mode}"')
            else:
                updated_lines.append(line)

        # Write updated settings
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines))

        print(f"Updated settings.toml with mode: {mode}")

    except Exception as e:
        print(f"Failed to update settings: {e}")


def create_default_settings(mode: str) -> None:
    """Create default settings file."""
    default_content = f"""# Mauscribe Settings
[general]
name = "Mauscribe"
version = "2.0"
debug = false

[recording_modes]
default_mode = "{mode}"

[recording_modes.normal]
auto_cleanup = true
cleanup_after_n_recordings = 10
cleanup_on_exit = true

[recording_modes.enhanced]
save_audio_files = true
save_audio_data_in_db = false
max_file_size_mb = 100
compression_enabled = true

[audio]
sample_rate = 16000
channels = 1
format = "wav"

[transcription]
model = "base"
language = "de"
confidence_threshold = 0.5

[ui]
theme = "cyberpunk"
notifications_enabled = true
control_center_enabled = true
"""

    with open("settings.toml", "w", encoding="utf-8") as f:
        f.write(default_content)


def show_current_mode() -> None:
    """Show current recording mode."""
    try:
        from src.utils.enhanced_database import get_enhanced_database

        db = get_enhanced_database()

        print("Current Mauscribe Status:")
        print(f"   Session ID: {db.current_session_id or 'None'}")
        print(f"   Recording Count: {db.recording_count}")

        # Check settings file
        settings_path = Path("settings.toml")
        if settings_path.exists():
            with open(settings_path, encoding="utf-8") as f:
                content = f.read()

            for line in content.split("\n"):
                if line.strip().startswith("default_mode ="):
                    mode = line.split("=")[1].strip().strip('"')
                    print(f"   Default Mode: {mode}")
                    break

        # Get recent recordings
        recordings = db.get_recordings_with_transcriptions(limit=5)
        print(f"   Recent Recordings: {len(recordings)}")

        if recordings:
            print("   Latest recordings:")
            for i, rec in enumerate(recordings[:3]):
                mode = rec.get("mode", "unknown")
                duration = rec.get("duration_seconds", 0)
                print(f"     {i+1}. {mode} mode, {duration:.1f}s")

    except Exception as e:
        print(f"Failed to get current status: {e}")


def main():
    """Main command line interface."""
    parser = argparse.ArgumentParser(description="Mauscribe Mode Switcher")
    parser.add_argument("command", choices=["switch", "status"], help="Command to execute")
    parser.add_argument("--mode", choices=["normal", "enhanced"], help="Mode to switch to")

    args = parser.parse_args()

    if args.command == "switch":
        if not args.mode:
            print("Please specify --mode (normal or enhanced)")
            return
        switch_mode(args.mode)

    elif args.command == "status":
        show_current_mode()


if __name__ == "__main__":
    main()
