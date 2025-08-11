#!/usr/bin/env python3
"""
Setup script for Mauscribe Git Hooks
Automatically installs post-commit and post-push hooks for pipeline monitoring
"""

import os
import shutil
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
    
    # Install hooks
    hooks_installed = 0
    for hook_file in templates_dir.glob("*"):
        if hook_file.is_file() and not hook_file.name.startswith("."):
            hook_name = hook_file.name
            target_hook = hooks_dir / hook_name
            
            try:
                # Copy hook file
                shutil.copy2(hook_file, target_hook)
                
                # Make executable (Unix-like systems)
                if os.name != 'nt':  # Not Windows
                    target_hook.chmod(target_hook.stat().st_mode | stat.S_IEXEC)
                
                print(f"✅ Installed {hook_name} hook")
                hooks_installed += 1
                
            except Exception as e:
                print(f"❌ Failed to install {hook_name} hook: {e}")
    
    if hooks_installed > 0:
        print(f"\n🎉 Successfully installed {hooks_installed} Git hooks!")
        print("💡 The hooks will now run automatically:")
        print("   - post-commit: Asks if you want to push and start pipeline monitoring")
        print("   - post-push: Automatically starts pipeline monitoring")
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
