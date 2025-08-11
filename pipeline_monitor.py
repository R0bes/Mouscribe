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

    def get_workflow_runs(self, branch: str, commit_sha: str) -> List[Dict]:
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

            response = requests.get(url, headers=headers, params=params)  # type: ignore
            response.raise_for_status()

            runs = response.json()["workflow_runs"]

            # Filter runs for the specific commit
            commit_runs = [run for run in runs if run["head_sha"] == commit_sha]
            return commit_runs

        except requests.RequestException as e:
            print(f"ERROR: Error fetching workflow runs: {e}")
            return []

    def get_workflow_details(self, workflow_id: int) -> Optional[Dict]:
        """Get detailed workflow information including jobs."""
        if not self.github_token:
            return None

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # First get the workflow run
            url = f"{self.base_url}/actions/runs/{workflow_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            workflow_run = response.json()

            # Then get the jobs using the jobs_url
            if "jobs_url" in workflow_run:
                jobs_response = requests.get(workflow_run["jobs_url"], headers=headers)
                jobs_response.raise_for_status()
                jobs = jobs_response.json()["jobs"]

                # Add jobs to the workflow run data
                workflow_run["jobs"] = jobs

            return workflow_run
        except requests.RequestException:
            return None

    def get_job_logs(self, workflow_id: int, job_id: int) -> Optional[str]:
        """Get logs for a specific job."""
        if not self.github_token:
            return None

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Try the jobs logs endpoint first
            url = f"{self.base_url}/actions/runs/{workflow_id}/jobs/{job_id}/logs"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                # Try alternative endpoint
                url = f"{self.base_url}/actions/jobs/{job_id}/logs"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text

            # If still not working, return error info
            print(f"   DEBUG: Logs API returned status {response.status_code}")
            print(f"   DEBUG: Response headers: {dict(response.headers)}")

            return None
        except requests.RequestException as e:
            print(f"   DEBUG: Request error: {e}")
            return None

    def _print_pipeline_header(
        self, current_branch: str, commit_sha: str, max_wait_time: int
    ) -> None:
        """Print pipeline monitoring header."""
        print("Mauscribe Pipeline Monitor")
        print("=" * 50)
        print(f"Branch: {current_branch}")
        print(f"Commit: {commit_sha[:8]}")
        print(f"Max wait time: {max_wait_time} seconds")
        print()

    def monitor_pipelines(self, max_wait_time: int = 300) -> bool:  # noqa: C901
        """Monitor pipeline execution and provide feedback."""
        current_branch = self.get_current_branch()
        commit_sha = self.get_last_commit_sha()

        if not commit_sha:
            print("ERROR: Could not determine commit SHA")
            return False

        self._print_pipeline_header(current_branch, commit_sha, max_wait_time)

        start_time = time.time()
        last_status = None

        while time.time() - start_time < max_wait_time:
            runs = self.get_workflow_runs(current_branch, commit_sha)

            if not runs:
                print("WAITING: Waiting for pipeline to start...")
                time.sleep(10)
                continue

            # Get the most recent run
            latest_run = runs[0]
            status = latest_run["status"]
            conclusion = latest_run.get("conclusion")

            # Only print if status changed
            if status != last_status:
                print(f"STATUS: {status}")
                if conclusion:
                    print(f"CONCLUSION: {conclusion}")
                print()
                last_status = status

            if status == "completed":
                if conclusion == "success":
                    print("SUCCESS: Pipeline completed successfully!")
                    self._show_success_summary(latest_run)
                    return True
                elif conclusion == "failure":
                    print("FAILED: Pipeline failed!")
                    self._show_failure_details(latest_run)
                    return False
                elif conclusion == "cancelled":
                    print("CANCELLED: Pipeline was cancelled")
                    return False
                else:
                    print(f"WARNING: Pipeline completed with conclusion: {conclusion}")
                    return False

            elif status == "in_progress":
                print("RUNNING: Pipeline is running...")
                self._show_progress(latest_run)

            elif status == "queued":
                print("QUEUED: Pipeline is queued...")

            elif status == "waiting":
                print("WAITING: Pipeline is waiting...")

            time.sleep(15)  # Check every 15 seconds

        print(f"TIMEOUT: Timeout reached after {max_wait_time} seconds")
        print("Pipeline may still be running. Check GitHub Actions manually.")
        return False

    def _show_success_summary(self, run: Dict):
        """Show summary of successful pipeline run."""
        print("\nSUCCESS: Pipeline Success Summary:")
        print("-" * 30)
        print(f"SUCCESS: Workflow: {run['name']}")
        print(
            f"DURATION: {self._format_duration(run['created_at'], run['updated_at'])}"
        )
        print(f"URL: {run['html_url']}")

        # Show job summary
        if "jobs_url" in run:
            try:
                headers = (
                    {"Authorization": f"token {self.github_token}"}
                    if self.github_token
                    else {}
                )
                response = requests.get(run["jobs_url"], headers=headers)
                if response.status_code == 200:
                    jobs = response.json()["jobs"]
                    print(f"\nJOBS: Jobs ({len(jobs)}):")
                    for job in jobs:
                        status_text = (
                            "SUCCESS" if job["conclusion"] == "success" else "FAILED"
                        )
                        print(f"  {status_text} {job['name']}: {job['conclusion']}")
            except Exception:
                pass

    def _show_failure_details(self, run: Dict):
        """Show detailed failure information including job logs."""
        print("\n❌ Pipeline Failure Details:")
        print("-" * 30)
        print(f"🔗 Workflow: {run['name']}")
        print(f"🔗 URL: {run['html_url']}")
        print(
            f"⏱️  Duration: {self._format_duration(run['created_at'], run['updated_at'])}"
        )
        print()

        # Get workflow details to see all jobs
        workflow_details = self.get_workflow_details(run["id"])
        if not workflow_details:
            print("WARNING: Could not fetch workflow details")
            return

        print(f"DEBUG: Workflow details keys: {list(workflow_details.keys())}")

        jobs = workflow_details.get("jobs", [])
        print(f"DEBUG: Found {len(jobs)} jobs")

        failed_jobs = [job for job in jobs if job.get("conclusion") == "failure"]
        print(f"DEBUG: Found {len(failed_jobs)} failed jobs")

        if failed_jobs:
            print(f"❌ Failed Jobs ({len(failed_jobs)}):")
            for job in failed_jobs:
                print(f"  FAILED: {job['name']}")
                print(f"     Started: {job['started_at']}")
                print(f"     Completed: {job['completed_at']}")

                # Fetch and display job logs
                print(f"\nLOGS: Job Logs for '{job['name']}':")
                print("-" * 40)
                logs = self.get_job_logs(run["id"], job["id"])
                if logs:
                    # Show last 20 lines of logs (most relevant for errors)
                    log_lines = logs.split("\n")
                    if len(log_lines) > 20:
                        print("... (showing last 20 lines)")
                        log_lines = log_lines[-20:]

                    for line in log_lines:
                        if line.strip():
                            print(f"   {line}")
                else:
                    print("   WARNING: Could not fetch job logs")
                print("-" * 40)
                print()
        else:
            print("WARNING: No failed jobs found in workflow details")
            # Show all jobs for debugging
            print("\nDEBUG: All jobs in workflow:")
            for i, job in enumerate(jobs):
                job_name = job.get("name", "Unknown")
                job_status = job.get("status", "Unknown")
                job_conclusion = job.get("conclusion", "Unknown")
                print(
                    f"  {i + 1}. {job_name} - Status: {job_status} - Conclusion: {job_conclusion}"
                )

        print("FAILED: Some pipelines failed. Check the details above.")

    def _show_progress(self, run: Dict):
        """Show progress of running pipeline."""
        if "jobs_url" in run:
            try:
                headers = (
                    {"Authorization": f"token {self.github_token}"}
                    if self.github_token
                    else {}
                )
                response = requests.get(run["jobs_url"], headers=headers)
                if response.status_code == 200:
                    jobs = response.json()["jobs"]
                    running_jobs = [
                        job for job in jobs if job["status"] == "in_progress"
                    ]
                    completed_jobs = [
                        job for job in jobs if job["status"] == "completed"
                    ]

                    if running_jobs:
                        print(
                            f"  RUNNING: {', '.join(job['name'] for job in running_jobs)}"
                        )
                    if completed_jobs:
                        print(f"  COMPLETED: {len(completed_jobs)}/{len(jobs)} jobs")
            except Exception:
                pass

    def _format_duration(self, created_at: str, updated_at: str) -> str:
        """Format duration between two timestamps."""
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            duration = updated - created

            if duration.total_seconds() < 60:
                return f"{int(duration.total_seconds())}s"
            elif duration.total_seconds() < 3600:
                minutes = int(duration.total_seconds() // 60)
                seconds = int(duration.total_seconds() % 60)
                return f"{minutes}m {seconds}s"
            else:
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                return f"{hours}h {minutes}m"
        except Exception:
            return "unknown"

    def open_pipeline_in_browser(self):
        """Open the pipeline status in the default browser."""
        commit_sha = self.get_last_commit_sha()

        if commit_sha:
            url = f"https://github.com/{self.repo_owner}/{self.repo_name}/actions"
            print(f"BROWSER: Opening pipeline status in browser: {url}")

            try:
                import webbrowser

                webbrowser.open(url)
            except ImportError:
                print("Could not open browser automatically")
                print(f"Please visit: {url}")


def main():
    """Main function for pipeline monitoring."""
    monitor = PipelineMonitor()

    # Check if we should open in browser
    if len(sys.argv) > 1 and sys.argv[1] == "--open":
        monitor.open_pipeline_in_browser()
        return

    # Monitor pipelines
    success = monitor.monitor_pipelines()

    if success:
        print("\nSUCCESS: All pipelines passed successfully!")
        sys.exit(0)
    else:
        print("\nFAILED: Some pipelines failed. Check the details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
