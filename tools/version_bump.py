#!/usr/bin/env python3
"""
Version Bump Tool for Mauscribe
Semantic versioning helper for automated version management.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import toml


class VersionBumper:
    """Handles semantic versioning for Mauscribe."""

    def __init__(self):
        """Initialize version bumper."""
        self.pyproject_path = Path("pyproject.toml")

    def get_current_version(self) -> str:
        """Get current version from pyproject.toml."""
        if not self.pyproject_path.exists():
            raise FileNotFoundError("pyproject.toml not found")

        data = toml.load(self.pyproject_path)
        return data["project"]["version"]

    def parse_version(self, version: str) -> tuple[int, int, int]:
        """Parse semantic version string."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")

        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Bump version based on type."""
        major, minor, patch = self.parse_version(current_version)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def update_pyproject(self, new_version: str) -> None:
        """Update version in pyproject.toml."""
        data = toml.load(self.pyproject_path)
        data["project"]["version"] = new_version

        with open(self.pyproject_path, "w") as f:
            toml.dump(data, f)

        print(f"[OK] Updated pyproject.toml: {new_version}")

    def create_git_tag(self, version: str) -> None:
        """Create git tag for version."""
        tag_name = f"v{version}"

        # Check if tag already exists
        try:
            subprocess.run(["git", "tag", "-l", tag_name], capture_output=True, check=True)
            if subprocess.run(["git", "tag", "-l", tag_name], capture_output=True).stdout.strip():
                print(f"[WARN] Tag {tag_name} already exists")
                return
        except subprocess.CalledProcessError:
            pass

        # Create and push tag
        try:
            subprocess.run(["git", "add", "pyproject.toml"], check=True)
            subprocess.run(["git", "commit", "-m", f"Bump version to {version}"], check=True)
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {version}"], check=True)
            subprocess.run(["git", "push", "origin", "HEAD"], check=True)
            subprocess.run(["git", "push", "origin", tag_name], check=True)

            print(f"[OK] Created and pushed tag: {tag_name}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to create tag: {e}")
            sys.exit(1)

    def bump_and_tag(self, bump_type: str) -> None:
        """Bump version and create git tag."""
        current_version = self.get_current_version()
        new_version = self.bump_version(current_version, bump_type)

        print(f"[INFO] Bumping version: {current_version} -> {new_version}")

        self.update_pyproject(new_version)
        self.create_git_tag(new_version)

        print(f"[SUCCESS] Version bump complete! New version: {new_version}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mauscribe Version Bumper")
    parser.add_argument("bump_type", choices=["major", "minor", "patch"], help="Type of version bump")

    args = parser.parse_args()

    try:
        bumper = VersionBumper()
        bumper.bump_and_tag(args.bump_type)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
