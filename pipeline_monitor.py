#!/usr/bin/env python3
"""Pipeline monitoring script for Mauscribe CI/CD pipelines."""

import subprocess
import time
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple

class PipelineMonitor:
    """Monitor CI/CD pipeline status and provide feedback."""
    
    def __init__(self):
        self.repo_owner = "R0bes"
        self.repo_name = "Mouscribe"
        self.github_token = self._get_github_token()
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or git config."""
        # Try environment variable first
        import os
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
            
        # Try git config
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'github.token'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
            
        # Try local git config
        try:
            result = subprocess.run(
                ['git', 'config', 'github.token'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
            
        return None
    
    def get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"
    
    def get_last_commit_sha(self) -> str:
        """Get the SHA of the last commit."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def get_workflow_runs(self, branch: str, commit_sha: str) -> List[Dict]:
        """Get workflow runs for a specific branch and commit."""
        if not self.github_token:
            print("⚠️  No GitHub token found. Cannot check pipeline status.")
            print("   Set GITHUB_TOKEN environment variable or configure git config github.token")
            return []
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # Get workflow runs for the specific commit
            url = f"{self.base_url}/actions/runs"
            params = {
                'branch': branch,
                'per_page': 10
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            runs = response.json()['workflow_runs']
            
            # Filter runs for the specific commit
            commit_runs = [run for run in runs if run['head_sha'] == commit_sha]
            return commit_runs
            
        except requests.RequestException as e:
            print(f"❌ Error fetching workflow runs: {e}")
            return []
    
    def get_workflow_details(self, workflow_id: int) -> Optional[Dict]:
        """Get detailed information about a specific workflow run."""
        if not self.github_token:
            return None
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            url = f"{self.base_url}/actions/runs/{workflow_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def get_job_logs(self, workflow_id: int, job_id: int) -> Optional[str]:
        """Get logs for a specific job."""
        if not self.github_token:
            return None
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            url = f"{self.base_url}/actions/runs/{workflow_id}/jobs/{job_id}/logs"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None
    
    def monitor_pipelines(self, max_wait_time: int = 300) -> bool:
        """Monitor pipeline execution and provide feedback."""
        print("🔍 Mauscribe Pipeline Monitor")
        print("=" * 50)
        
        current_branch = self.get_current_branch()
        commit_sha = self.get_last_commit_sha()
        
        print(f"📋 Branch: {current_branch}")
        print(f"🔗 Commit: {commit_sha[:8]}")
        print(f"⏱️  Max wait time: {max_wait_time} seconds")
        print()
        
        if not commit_sha:
            print("❌ Could not determine commit SHA")
            return False
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait_time:
            runs = self.get_workflow_runs(current_branch, commit_sha)
            
            if not runs:
                print("⏳ Waiting for pipeline to start...")
                time.sleep(10)
                continue
            
            # Get the most recent run
            latest_run = runs[0]
            status = latest_run['status']
            conclusion = latest_run.get('conclusion')
            
            # Only print if status changed
            if status != last_status:
                print(f"🔄 Status: {status}")
                if conclusion:
                    print(f"📊 Conclusion: {conclusion}")
                print()
                last_status = status
            
            if status == 'completed':
                if conclusion == 'success':
                    print("✅ Pipeline completed successfully!")
                    self._show_success_summary(latest_run)
                    return True
                elif conclusion == 'failure':
                    print("❌ Pipeline failed!")
                    self._show_failure_details(latest_run)
                    return False
                elif conclusion == 'cancelled':
                    print("⏹️  Pipeline was cancelled")
                    return False
                else:
                    print(f"⚠️  Pipeline completed with conclusion: {conclusion}")
                    return False
            
            elif status == 'in_progress':
                print("⚡ Pipeline is running...")
                self._show_progress(latest_run)
            
            elif status == 'queued':
                print("⏳ Pipeline is queued...")
            
            elif status == 'waiting':
                print("⏳ Pipeline is waiting...")
            
            time.sleep(15)  # Check every 15 seconds
        
        print(f"⏰ Timeout reached after {max_wait_time} seconds")
        print("Pipeline may still be running. Check GitHub Actions manually.")
        return False
    
    def _show_success_summary(self, run: Dict):
        """Show summary of successful pipeline run."""
        print("\n🎉 Pipeline Success Summary:")
        print("-" * 30)
        print(f"✅ Workflow: {run['name']}")
        print(f"⏱️  Duration: {self._format_duration(run['created_at'], run['updated_at'])}")
        print(f"🔗 URL: {run['html_url']}")
        
        # Show job summary
        if 'jobs_url' in run:
            try:
                headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
                response = requests.get(run['jobs_url'], headers=headers)
                if response.status_code == 200:
                    jobs = response.json()['jobs']
                    print(f"\n📋 Jobs ({len(jobs)}):")
                    for job in jobs:
                        status_emoji = "✅" if job['conclusion'] == 'success' else "❌"
                        print(f"  {status_emoji} {job['name']}: {job['conclusion']}")
            except:
                pass
    
    def _show_failure_details(self, run: Dict):
        """Show detailed failure information."""
        print("\n❌ Pipeline Failure Details:")
        print("-" * 30)
        print(f"🔗 Workflow: {run['name']}")
        print(f"🔗 URL: {run['html_url']}")
        
        # Get detailed workflow information
        workflow_details = self.get_workflow_details(run['id'])
        if workflow_details:
            print(f"⏱️  Duration: {self._format_duration(run['created_at'], run['updated_at'])}")
            
            # Show failed jobs
            if 'jobs_url' in run:
                try:
                    headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
                    response = requests.get(run['jobs_url'], headers=headers)
                    if response.status_code == 200:
                        jobs = response.json()['jobs']
                        failed_jobs = [job for job in jobs if job['conclusion'] == 'failure']
                        
                        if failed_jobs:
                            print(f"\n❌ Failed Jobs ({len(failed_jobs)}):")
                            for job in failed_jobs:
                                print(f"  🔥 {job['name']}")
                                print(f"     Started: {job['started_at']}")
                                print(f"     Completed: {job['completed_at']}")
                                
                                # Try to get job logs
                                if 'id' in job:
                                    logs = self.get_job_logs(run['id'], job['id'])
                                    if logs:
                                        # Extract error summary from logs
                                        error_lines = [line for line in logs.split('\n') if 'ERROR' in line or 'FAILED' in line]
                                        if error_lines:
                                            print(f"     Recent errors:")
                                            for error in error_lines[-3:]:  # Last 3 error lines
                                                print(f"       {error.strip()}")
                                        else:
                                            print(f"     Check logs at: {job['html_url']}")
                except Exception as e:
                    print(f"     Could not fetch job details: {e}")
    
    def _show_progress(self, run: Dict):
        """Show progress of running pipeline."""
        if 'jobs_url' in run:
            try:
                headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
                response = requests.get(run['jobs_url'], headers=headers)
                if response.status_code == 200:
                    jobs = response.json()['jobs']
                    running_jobs = [job for job in jobs if job['status'] == 'in_progress']
                    completed_jobs = [job for job in jobs if job['status'] == 'completed']
                    
                    if running_jobs:
                        print(f"  🚀 Running: {', '.join(job['name'] for job in running_jobs)}")
                    if completed_jobs:
                        print(f"  ✅ Completed: {len(completed_jobs)}/{len(jobs)} jobs")
            except:
                pass
    
    def _format_duration(self, created_at: str, updated_at: str) -> str:
        """Format duration between two timestamps."""
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
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
        except:
            return "unknown"
    
    def open_pipeline_in_browser(self):
        """Open the pipeline status in the default browser."""
        current_branch = self.get_current_branch()
        commit_sha = self.get_last_commit_sha()
        
        if commit_sha:
            url = f"https://github.com/{self.repo_owner}/{self.repo_name}/actions"
            print(f"🌐 Opening pipeline status in browser: {url}")
            
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
    if len(sys.argv) > 1 and sys.argv[1] == '--open':
        monitor.open_pipeline_in_browser()
        return
    
    # Monitor pipelines
    success = monitor.monitor_pipelines()
    
    if success:
        print("\n🎉 All pipelines passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some pipelines failed. Check the details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
