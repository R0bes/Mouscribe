#!/usr/bin/env python3
"""
Setup script for Mauscribe Git Hooks
Automatically installs pre-commit and pre-push hooks
"""

import os
import stat
import sys
from pathlib import Path


def setup_git_hooks():
    """Install Git hooks from templates directory"""
    print("🚀 Setting up Mauscribe Git Hooks...")

    # Get repository root
    repo_root = Path(__file__).parent
    hooks_dir = repo_root / ".git" / "hooks"
    templates_dir = repo_root / "templates"

    # Check if we're in a Git repository
    if not hooks_dir.exists():
        print("❌ Error: Not in a Git repository")
        print("💡 Please run this script from the root of a Git repository")
        return False

    # Check if templates exist
    if not templates_dir.exists():
        print("❌ Error: Templates directory not found")
        print("💡 Please ensure the templates directory exists")
        return False

    # Define which hooks to install
    hook_files = ["pre-commit", "pre-push"]

    # Install hooks
    hooks_installed = 0
    for hook_name in hook_files:
        hook_file = templates_dir / hook_name

        if hook_file.exists():
            target_hook = hooks_dir / hook_name

            try:
                # Read the template file and convert line endings
                with open(hook_file, encoding="utf-8") as f:
                    content = f.read()

                # Convert Windows line endings to Unix line endings
                content = content.replace("\r\n", "\n")

                # Write the hook with correct line endings
                with open(target_hook, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)

                # Make executable (Unix-like systems)
                if os.name != "nt":  # Not Windows
                    target_hook.chmod(target_hook.stat().st_mode | stat.S_IEXEC)

                print(f"✅ Installed {hook_name} hook")
                hooks_installed += 1

            except Exception as e:
                print(f"❌ Failed to install {hook_name} hook: {e}")
        else:
            print(f"⚠️  Hook file {hook_name} not found in templates")

    if hooks_installed > 0:
        print(f"🎉 Successfully installed {hooks_installed} Git hooks!")
        print("💡 The hooks will now run automatically:")
        print("   - pre-commit: Runs linting and code quality checks")
        print("   - pre-push: Runs tests and starts pipeline monitoring")
        return True
    else:
        print("❌ No hooks were installed")
        return False


def main():
    """Main function"""
    try:
        success = setup_git_hooks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
