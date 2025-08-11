# build.py - Mauscribe Build Script for creating .exe file with icon
#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def main():
    print("Mauscribe Build Script")
    print("=" * 40)

    # Check if PyInstaller is installed
    try:
        import PyInstaller

        print("PyInstaller found")
    except ImportError:
        print("PyInstaller not found")
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check if icon exists
    icon_path = Path("icons/mauscribe_icon.ico")
    if icon_path.exists():
        print(f"Icon found: {icon_path}")
        icon_arg = f"--icon={icon_path}"
    else:
        print("Icon not found, using default icon")
        icon_arg = ""

    # Clean old build files
    print("Cleaning old build files...")
    if Path("dist").exists():
        import shutil

        shutil.rmtree("dist")
    if Path("build").exists():
        import shutil

        shutil.rmtree("build")
    if Path("mauscribe.spec").exists():
        Path("mauscribe.spec").unlink()

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Single .exe file
        "--windowed",  # No console window
        "--name=mauscribe",  # .exe name
        "--clean",  # Clean build
        "--hidden-import=spellchecker",  # Explicitly include pyspellchecker
        "--hidden-import=requests",  # Explicitly include requests
        "--collect-data=spellchecker",  # Include data files
        "main.py",  # Main file
    ]

    # Add icon if available
    if icon_arg:
        cmd.insert(-1, icon_arg)

    print("Starting build...")
    print(f"Command: {' '.join(cmd)}")

    # Execute build
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Build successful!")

        # Check if .exe was created
        exe_path = Path("dist/mauscribe.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f".exe created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")

            # Test the .exe
            print("Testing .exe...")
            try:
                test_result = subprocess.run(
                    [str(exe_path), "--help"], capture_output=True, text=True, timeout=5
                )
                print(".exe works")
            except subprocess.TimeoutExpired:
                print(".exe starts (Timeout = OK)")
            except Exception as e:
                print(f".exe test: {e}")
        else:
            print(".exe was not created")
    else:
        print("Build failed!")
        print("Error:")
        print(result.stderr)

    print("=" * 40)
    print("Build completed!")


if __name__ == "__main__":
    main()
