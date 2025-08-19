#!/usr/bin/env python3
"""Test script for pipeline monitor debugging."""

from pipeline_monitor import PipelineMonitor

def test_workflow_runs():
    """Test getting workflow runs."""
    monitor = PipelineMonitor()
    
    print("Testing workflow runs...")
    
    # Get current branch
    branch = monitor.get_current_branch()
    print(f"Current branch: {branch}")
    
    # Get workflow runs for the branch
    runs = monitor.get_workflow_runs(branch, "")
    print(f"\nWorkflow runs found: {len(runs)}")
    
    for i, run in enumerate(runs[:5]):  # Show first 5 runs
        print(f"\nRun {i+1}:")
        print(f"  ID: {run.get('id')}")
        print(f"  Name: {run.get('name')}")
        print(f"  Status: {run.get('status')}")
        print(f"  Conclusion: {run.get('conclusion')}")
        print(f"  Commit: {run.get('head_sha', '')[:8]}")
        print(f"  Created: {run.get('created_at')}")
        
        # Check if this run has jobs
        details = monitor.get_workflow_details(run.get('id'))
        if details:
            jobs = details.get('jobs', [])
            print(f"  Jobs: {len(jobs)}")
            
            if jobs:
                print("  Job details:")
                for j, job in enumerate(jobs):
                    print(f"    Job {j+1}: {job.get('name')} - {job.get('status')} - {job.get('conclusion')}")
                    
                    # Try to get logs for failed jobs
                    if job.get('conclusion') == 'failure':
                        print(f"    Getting logs for failed job '{job.get('name')}'...")
                        logs = monitor.get_job_logs(run.get('id'), job.get('name'))
                        print(f"    Logs found: {len(logs)} lines")
                        if logs:
                            print(f"    First few log lines:")
                            for line in logs[:3]:
                                print(f"      {line}")
        else:
            print("  ❌ Could not get workflow details")

if __name__ == "__main__":
    test_workflow_runs()
