#!/usr/bin/env python3
"""Pipeline monitoring script for Mauscribe CI/CD pipelines."""

import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests


class PipelineMonitor:
    """Monitor CI/CD pipeline status and provide feedback."""

    def __init__(self):
        self.repo_owner = "R0bes"
        self.repo_name = "Mouscribe"
        self.github_token = self._get_github_token()
        self.base_url = (
            f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        )
        # Updated workflow name for the unified pipeline
        self.workflow_name = "CI/CD Pipeline"

    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or git config."""
        # Try environment variable first
        import os

        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

        # Try git config
        try:
            result = subprocess.run(
                ["git", "config", "--global", "github.token"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        # Try local git config
        try:
            result = subprocess.run(
                ["git", "config", "github.token"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

        return None

    def get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"

    def get_last_commit_sha(self) -> str:
        """Get the SHA of the last commit."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def get_workflow_runs(self, branch: str, commit_sha: str) -> list[dict]:
        """Get workflow runs for a specific branch and commit."""
        if not self.github_token:
            print("WARNING: No GitHub token found. Cannot check pipeline status.")
            print(
                "   Set GITHUB_TOKEN environment variable or configure git config github.token"
            )
            return []

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Get workflow runs for the specific commit
            url = f"{self.base_url}/actions/runs"
            params = {"branch": branch, "per_page": 10}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            runs = response.json().get("workflow_runs", [])
            
            # Filter for our unified CI/CD pipeline
            filtered_runs = [
                run for run in runs 
                if run.get("name") == self.workflow_name
            ]
            
            return filtered_runs

        except requests.RequestException as e:
            print(f"Error fetching workflow runs: {e}")
            return []

    def get_workflow_details(self, workflow_id: int) -> Optional[dict]:
        """Get detailed information about a specific workflow run."""
        if not self.github_token:
            return None

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            url = f"{self.base_url}/actions/runs/{workflow_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching workflow details: {e}")
            return None

    def get_job_logs(self, workflow_id: int, job_name: str) -> List[str]:
        """Get logs for a specific job in a workflow run."""
        if not self.github_token:
            return []

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Get jobs for the workflow
            url = f"{self.base_url}/actions/runs/{workflow_id}/jobs"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            jobs = response.json().get("jobs", [])
            target_job = None

            for job in jobs:
                if job.get("name") == job_name:
                    target_job = job
                    break

            if not target_job:
                return []

            # Get logs for the job
            logs_url = target_job.get("logs_url")
            if not logs_url:
                return []

            response = requests.get(logs_url, headers=headers)
            response.raise_for_status()

            # Parse logs (GitHub returns logs as plain text)
            log_lines = response.text.split("\n")
            
            # Extract error details from logs
            error_lines = []
            for line in log_lines:
                line = line.strip()
                if line:
                    # Look for common error patterns
                    if any(keyword in line.lower() for keyword in [
                        "error", "failed", "failure", "exception", "traceback", 
                        "syntax error", "import error", "module not found",
                        "command not found", "exit code", "returned exit code"
                    ]):
                        error_lines.append(line)
            
            # If we found specific errors, return them; otherwise return last lines
            if error_lines:
                return error_lines[:10]  # Return up to 10 error lines
            else:
                return log_lines[-15:]  # Return last 15 lines if no specific errors found

        except requests.RequestException as e:
            print(f"Error fetching job logs: {e}")
            return []

    def extract_error_summary(self, logs: List[str]) -> str:
        """Extract a summary of the most important error from logs."""
        if not logs:
            return "No logs available"
        
        # Look for the most critical error patterns
        for line in logs:
            line_lower = line.lower()
            
            # Python-specific errors
            if "syntaxerror:" in line_lower:
                return f"Syntax Error: {line.strip()}"
            elif "importerror:" in line_lower:
                return f"Import Error: {line.strip()}"
            elif "modulenotfounderror:" in line_lower:
                return f"Module Not Found: {line.strip()}"
            elif "attributeerror:" in line_lower:
                return f"Attribute Error: {line.strip()}"
            elif "typeerror:" in line_lower:
                return f"Type Error: {line.strip()}"
            elif "nameerror:" in line_lower:
                return f"Name Error: {line.strip()}"
            
            # General errors
            elif "error:" in line_lower:
                return f"Error: {line.strip()}"
            elif "failed:" in line_lower:
                return f"Failed: {line.strip()}"
            elif "exception:" in line_lower:
                return f"Exception: {line.strip()}"
            
            # Exit codes
            elif "returned exit code" in line_lower:
                return f"Process Failed: {line.strip()}"
        
        # If no specific error pattern found, return the first non-empty line
        for line in logs:
            if line.strip():
                return f"Log Entry: {line.strip()}"
        
        return "Unknown error occurred"

    def monitor_pipeline(self, max_wait_time: int = 300) -> bool:
        """Monitor the CI/CD pipeline for the current branch."""
        print("Mauscribe Pipeline Monitor")
        print("=" * 50)

        current_branch = self.get_current_branch()
        last_commit = self.get_last_commit_sha()[:8]

        print(f"Branch: {current_branch}")
        print(f"Commit: {last_commit}")
        print(f"Max wait time: {max_wait_time} seconds")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < max_wait_time:
            workflow_runs = self.get_workflow_runs(current_branch, last_commit)

            if not workflow_runs:
                print("No workflow runs found for current branch/commit")
                return False

            latest_run = workflow_runs[0]
            status = latest_run.get("status", "unknown")
            conclusion = latest_run.get("conclusion")

            # Only print status if it changed
            if status != last_status:
                print(f"\nSTATUS: {status}")
                if conclusion:
                    print(f"CONCLUSION: {conclusion}")

                if status == "completed":
                    if conclusion == "success":
                        print("\n✅ Pipeline succeeded!")
                        return True
                    elif conclusion == "failure":
                        print("\n❌ Pipeline failed!")
                        self._show_failure_details(latest_run)
                        return False
                    elif conclusion == "cancelled":
                        print("\n⚠️  Pipeline was cancelled")
                        return False
                elif status == "in_progress":
                    print("\nRUNNING: Pipeline is running...")
                    self._show_running_jobs(latest_run)
                elif status == "queued":
                    print("\n⏳ Pipeline is queued...")
                elif status == "waiting":
                    print("\n⏳ Pipeline is waiting...")

                last_status = status

            time.sleep(15)  # Check every 15 seconds

        print(f"\n⏰ Timeout after {max_wait_time} seconds")
        return False

    def _show_running_jobs(self, workflow_run: dict) -> None:
        """Show currently running jobs."""
        workflow_id = workflow_run.get("id")
        if not workflow_id:
            return

        workflow_details = self.get_workflow_details(workflow_id)
        if not workflow_details:
            return

        jobs = workflow_details.get("jobs", [])
        running_jobs = [job for job in jobs if job.get("status") == "in_progress"]

        for job in running_jobs:
            print(f"  RUNNING: {job.get('name', 'Unknown Job')}")

    def _show_failure_details(self, workflow_run: dict) -> None:
        """Show detailed information about pipeline failure."""
        workflow_id = workflow_run.get("id")
        if not workflow_id:
            return

        workflow_details = self.get_workflow_details(workflow_id)
        if not workflow_details:
            return

        print("\n❌ Pipeline Failure Details:")
        print("-" * 30)
        print(f"🔗 Workflow: {workflow_details.get('name', 'Unknown')}")
        print(f"🔗 URL: {workflow_details.get('html_url', 'N/A')}")
        
        # Calculate duration
        created_at = workflow_details.get("created_at")
        updated_at = workflow_details.get("updated_at")
        if created_at and updated_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                duration = updated - created
                print(f"⏱️  Duration: {duration}")
            except ValueError:
                pass

        # Show job status
        jobs = workflow_details.get("jobs", [])
        failed_jobs = [job for job in jobs if job.get("conclusion") == "failure"]

        if failed_jobs:
            print(f"\n❌ Failed Jobs ({len(failed_jobs)}):")
            for job in failed_jobs:
                job_name = job.get("name", "Unknown")
                started_at = job.get("started_at", "")
                completed_at = job.get("completed_at", "")
                
                print(f"\n  🔴 FAILED: {job_name}")
                if started_at:
                    print(f"     Started: {started_at}")
                if completed_at:
                    print(f"     Completed: {completed_at}")

                # Show job logs and extract error summary
                logs = self.get_job_logs(workflow_id, job_name)
                if logs:
                    # Extract error summary
                    error_summary = self.extract_error_summary(logs)
                    print(f"\n     💥 Error Summary: {error_summary}")
                    
                    # Show detailed logs
                    print(f"\n     📋 Detailed Logs for '{job_name}':")
                    print("     " + "-" * 40)
                    for line in logs:
                        if line.strip():
                            # Truncate very long lines
                            if len(line) > 120:
                                line = line[:117] + "..."
                            print(f"     {line}")
                else:
                    print(f"     ⚠️  No logs available for this job")

        print("\n💡 Check the GitHub Actions tab for more details")
        print(f"🔗 Direct Link: {workflow_details.get('html_url', 'N/A')}")

    def open_pipeline_in_browser(self) -> None:
        """Open the pipeline status in the default browser."""
        current_branch = self.get_current_branch()
        workflow_runs = self.get_workflow_runs(current_branch, "")

        if not workflow_runs:
            print("No workflow runs found")
            return

        latest_run = workflow_runs[0]
        html_url = latest_run.get("html_url")

        if html_url:
            import webbrowser
            webbrowser.open(html_url)
            print(f"Opened pipeline status in browser: {html_url}")
        else:
            print("Could not determine pipeline URL")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Mauscribe CI/CD pipelines")
    parser.add_argument(
        "--open", action="store_true", help="Open pipeline status in browser"
    )
    parser.add_argument(
        "--timeout", type=int, default=300, help="Maximum wait time in seconds"
    )

    args = parser.parse_args()

    monitor = PipelineMonitor()

    if args.open:
        monitor.open_pipeline_in_browser()
    else:
        success = monitor.monitor_pipeline(args.timeout)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
