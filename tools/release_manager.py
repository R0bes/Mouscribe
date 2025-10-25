#!/usr/bin/env python3
"""
Release Manager for Mauscribe
Automated GitHub release creation with changelog generation.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import toml


class ReleaseManager:
    """Manages GitHub releases with automated changelog generation."""

    def __init__(self, config_path: str = "tools/release_config.toml"):
        """Initialize release manager with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = "R0bes"
        self.repo_name = "Mauscribe"

    def _load_config(self) -> dict:
        """Load release configuration."""
        if self.config_path.exists():
            return toml.load(self.config_path)
        return {
            "release": {
                "template": "## What's New\n\n{changelog}\n\n## Installation\n\nDownload `Mauscribe.exe` from the assets below.",
                "changelog_format": "### {type}: {message}",
                "asset_patterns": ["dist/Mauscribe.exe", "dist/data/"],
            }
        }

    def get_latest_tag(self) -> Optional[str]:
        """Get the latest git tag."""
        try:
            result = subprocess.run(["git", "tag", "--sort=-version:refname"], capture_output=True, text=True, check=True)
            tags = result.stdout.strip().split("\n")
            return tags[0] if tags and tags[0] else None
        except subprocess.CalledProcessError:
            return None

    def get_commits_since_tag(self, tag: str) -> list[dict]:
        """Get commits since the given tag."""
        try:
            result = subprocess.run(
                ["git", "log", f"{tag}..HEAD", "--pretty=format:%H|%s|%an|%ad", "--date=short"],
                capture_output=True,
                text=True,
                check=True,
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    commits.append({"hash": parts[0], "message": parts[1], "author": parts[2], "date": parts[3]})
            return commits
        except subprocess.CalledProcessError:
            return []

    def categorize_commits(self, commits: list[dict]) -> dict[str, list[str]]:
        """Categorize commits by type."""
        categories = {"Features": [], "Bug Fixes": [], "Improvements": [], "Documentation": [], "Other": []}

        for commit in commits:
            message = commit["message"]

            # Categorize based on commit message patterns
            if re.match(r"^(feat|feature):", message, re.IGNORECASE):
                categories["Features"].append(message)
            elif re.match(r"^(fix|bug):", message, re.IGNORECASE):
                categories["Bug Fixes"].append(message)
            elif re.match(r"^(docs|doc):", message, re.IGNORECASE):
                categories["Documentation"].append(message)
            elif re.match(r"^(improve|refactor|perf):", message, re.IGNORECASE):
                categories["Improvements"].append(message)
            else:
                categories["Other"].append(message)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def generate_changelog(self, tag: str) -> str:
        """Generate changelog from commits since tag."""
        commits = self.get_commits_since_tag(tag)
        if not commits:
            return "No changes since last release."

        categorized = self.categorize_commits(commits)

        changelog_lines = []
        for category, messages in categorized.items():
            if messages:
                changelog_lines.append(f"### {category}")
                for message in messages:
                    # Clean up commit message
                    clean_message = re.sub(
                        r"^(feat|feature|fix|bug|docs|doc|improve|refactor|perf):\s*", "", message, flags=re.IGNORECASE
                    )
                    changelog_lines.append(f"- {clean_message}")
                changelog_lines.append("")

        return "\n".join(changelog_lines)

    def create_release_notes(self, tag: str, changelog: str) -> str:
        """Create release notes using template."""
        template = self.config["release"]["template"]
        return template.format(changelog=changelog, tag=tag, date=datetime.now().strftime("%Y-%m-%d"))

    def upload_assets(self, release_id: int, asset_paths: list[str]) -> None:
        """Upload assets to GitHub release."""
        if not self.github_token:
            print("❌ GITHUB_TOKEN not set, skipping asset upload")
            return

        headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}

        for asset_path in asset_paths:
            path = Path(asset_path)
            if not path.exists():
                print(f"⚠️ Asset not found: {asset_path}")
                continue

            if path.is_file():
                self._upload_file(headers, release_id, path)
            elif path.is_dir():
                # Upload directory contents
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        self._upload_file(headers, release_id, file_path)

    def _upload_file(self, headers: dict, release_id: int, file_path: Path) -> None:
        """Upload a single file to GitHub release."""
        url = f"https://uploads.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/{release_id}/assets"

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            params = {"name": file_path.name}

            response = requests.post(url, headers=headers, files=files, params=params)

            if response.status_code == 201:
                print(f"✅ Uploaded: {file_path.name}")
            else:
                print(f"❌ Failed to upload {file_path.name}: {response.status_code}")

    def create_release(self, tag: str, upload_assets: bool = False) -> None:
        """Create GitHub release."""
        if not self.github_token:
            print("❌ GITHUB_TOKEN environment variable not set")
            sys.exit(1)

        latest_tag = self.get_latest_tag()
        if not latest_tag:
            print("❌ No previous tag found")
            sys.exit(1)

        changelog = self.generate_changelog(latest_tag)
        release_notes = self.create_release_notes(tag, changelog)

        print(f"[INFO] Creating release for tag: {tag}")
        print("[INFO] Changelog preview:")
        print(changelog)
        print("-" * 50)

        # Create release via GitHub API
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
        headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}

        data = {"tag_name": tag, "name": f"Mauscribe {tag}", "body": release_notes, "draft": False, "prerelease": False}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            release_data = response.json()
            print(f"✅ Release created: {release_data['html_url']}")

            if upload_assets:
                asset_paths = self.config["release"]["asset_patterns"]
                self.upload_assets(release_data["id"], asset_paths)
        else:
            print(f"❌ Failed to create release: {response.status_code}")
            print(response.text)
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mauscribe Release Manager")
    parser.add_argument("--tag", required=True, help="Git tag for release")
    parser.add_argument("--upload", action="store_true", help="Upload assets")
    parser.add_argument("--config", default="tools/release_config.toml", help="Config file path")

    args = parser.parse_args()

    manager = ReleaseManager(args.config)
    manager.create_release(args.tag, args.upload)


if __name__ == "__main__":
    main()
