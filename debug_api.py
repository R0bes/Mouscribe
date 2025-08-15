#!/usr/bin/env python3
"""Debug script to check GitHub API responses for workflow logs."""

import requests
import json

def debug_github_api():
    """Debug GitHub API responses for workflow logs."""
    
    # GitHub repository info
    repo_owner = "R0bes"
    repo_name = "Mouscribe"
    workflow_run_id = 16991462394
    
    # Try to get GitHub token
    import os
    import subprocess
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        try:
            result = subprocess.run(
                ["git", "config", "--global", "github.token"],
                capture_output=True,
                text=True,
                check=True,
            )
            token = result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
    
    if not token:
        print("❌ No GitHub token found!")
        print("   Set GITHUB_TOKEN environment variable or configure git config github.token")
        return
    
    print(f"✅ Using GitHub token: {token[:10]}...")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    # 1. Check workflow run details
    print(f"\n🔍 1. Checking workflow run {workflow_run_id}...")
    try:
        url = f"{base_url}/actions/runs/{workflow_run_id}"
        response = requests.get(url, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            run_data = response.json()
            print(f"   ✅ Workflow run found")
            print(f"   Name: {run_data.get('name')}")
            print(f"   Status: {run_data.get('status')}")
            print(f"   Conclusion: {run_data.get('conclusion')}")
            print(f"   HTML URL: {run_data.get('html_url')}")
        else:
            print(f"   ❌ Failed to get workflow run: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Check jobs for this workflow run
    print(f"\n🔍 2. Checking jobs for workflow run {workflow_run_id}...")
    try:
        url = f"{base_url}/actions/runs/{workflow_run_id}/jobs"
        response = requests.get(url, headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = jobs_data.get("jobs", [])
            print(f"   ✅ Found {len(jobs)} jobs")
            
            for i, job in enumerate(jobs):
                print(f"\n   Job {i+1}:")
                print(f"     ID: {job.get('id')}")
                print(f"     Name: {job.get('name')}")
                print(f"     Status: {job.get('status')}")
                print(f"     Conclusion: {job.get('conclusion')}")
                print(f"     Started: {job.get('started_at')}")
                print(f"     Completed: {job.get('completed_at')}")
                print(f"     Logs URL: {job.get('logs_url')}")
                
                # Check if logs URL is accessible
                if job.get("logs_url"):
                    print(f"     🔍 Testing logs URL...")
                    try:
                        logs_response = requests.get(job.get("logs_url"), headers=headers)
                        print(f"        Logs Status: {logs_response.status_code}")
                        if logs_response.status_code == 200:
                            print(f"        ✅ Logs accessible via API")
                            print(f"        Logs Length: {len(logs_response.text)} characters")
                            
                            # Show first few lines
                            lines = logs_response.text.split("\n")[:5]
                            print(f"        First 5 lines:")
                            for line in lines:
                                if line.strip():
                                    print(f"          {line}")
                        else:
                            print(f"        ❌ Logs not accessible: {logs_response.text}")
                    except Exception as e:
                        print(f"        ❌ Error accessing logs: {e}")
                else:
                    print(f"     ❌ No logs URL available")
        else:
            print(f"   ❌ Failed to get jobs: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 3. Check if we need different permissions
    print(f"\n🔍 3. Checking token permissions...")
    try:
        url = "https://api.github.com/user"
        response = requests.get(url, headers=headers)
        print(f"   User API Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Authenticated as: {user_data.get('login')}")
            print(f"   User ID: {user_data.get('id')}")
        else:
            print(f"   ❌ Authentication failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_github_api()
