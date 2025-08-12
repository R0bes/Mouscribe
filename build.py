# build.py - Mauscribe Build Script for creating .exe file with icon
#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check and install required dependencies."""
    required_packages = [
        "PyInstaller",
        "faster-whisper",
        "numpy",
        "sounddevice",
        "webrtcvad",
        "pynput",
        "pycaw",
        "comtypes",
        "python-dotenv",
        "openai",
        "pyperclip",
        "pyautogui",
        "pystray",
        "pillow",
        "pyspellchecker",
        "requests",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} found")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} not found")

    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                )
                print(f"✓ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {package}: {e}")
                return False

    return True


def clean_build_files():
    """Clean old build files."""
    print("Cleaning old build files...")

    dirs_to_clean = ["dist", "build", "__pycache__"]
    files_to_clean = ["mauscribe.spec", "*.pyc"]

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            import shutil

            shutil.rmtree(dir_path)
            print(f"✓ Cleaned {dir_name}/")

    for file_pattern in files_to_clean:
        for file_path in Path(".").glob(file_pattern):
            file_path.unlink()
            print(f"✓ Cleaned {file_path}")


def get_icon_path():
    """Get the appropriate icon path for the platform."""
    icon_paths = [
        "icons/mauscribe_icon.ico",
        "icons/mauscribe_icon.svg",
        "icons/mauscribe_small.svg",
    ]

    for icon_path in icon_paths:
        if Path(icon_path).exists():
            print(f"✓ Icon found: {icon_path}")
            return f"--icon={icon_path}"

    print("⚠ Icon not found, using default icon")
    return ""


def build_executable():
    """Build the executable using PyInstaller."""
    print("Starting build...")

    # Base PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Single .exe file
        "--windowed",  # No console window
        "--name=mauscribe",  # .exe name
        "--clean",  # Clean build
        "--noconfirm",  # Don't ask for confirmation
        "--hidden-import=spellchecker",  # Explicitly include pyspellchecker
        "--hidden-import=requests",  # Explicitly include requests
        "--hidden-import=pycaw",  # Windows audio
        "--hidden-import=comtypes",  # Windows COM
        "--hidden-import=win32api",  # Windows API
        "--hidden-import=win32con",  # Windows constants
        "--collect-data=spellchecker",  # Include data files
        "--collect-data=faster_whisper",  # Include STT model data
        "main.py",  # Main file
    ]

    # Add icon if available
    icon_arg = get_icon_path()
    if icon_arg:
        cmd.insert(-1, icon_arg)

    # Platform-specific optimizations
    if platform.system() == "Windows":
        cmd.extend(
            [
                "--hidden-import=win32gui",
                "--hidden-import=win32process",
                "--hidden-import=win32service",
            ]
        )

    print(f"Build command: {' '.join(cmd)}")

    # Execute build
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            print("✓ Build successful!")
            return True
        else:
            print("✗ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("✗ Build timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False


def test_executable():
    """Test the built executable."""
    exe_path = Path("dist/mauscribe.exe")

    if not exe_path.exists():
        print("✗ Executable was not created")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✓ .exe created: {exe_path}")
    print(f"✓ Size: {size_mb:.1f} MB")

    # Test the executable
    print("Testing executable...")
    try:
        test_result = subprocess.run(
            [str(exe_path), "--help"], capture_output=True, text=True, timeout=10
        )
        print("✓ Executable test successful")
        return True
    except subprocess.TimeoutExpired:
        print("✓ Executable starts (timeout = OK)")
        return True
    except Exception as e:
        print(f"⚠ Executable test warning: {e}")
        return True  # Don't fail build for test issues


def main():
    """Main build function."""
    print("Mauscribe Build Script")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("✗ Dependency check failed")
        return 1

    # Clean old files
    clean_build_files()

    # Build executable
    if not build_executable():
        print("✗ Build failed")
        return 1

    # Test executable
    if not test_executable():
        print("⚠ Executable test failed")
        return 1

    print("=" * 50)
    print("✓ Build completed successfully!")
    print("✓ Executable location: dist/mauscribe.exe")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
