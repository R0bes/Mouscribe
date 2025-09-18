#!/usr/bin/env python3
"""
Pipeline Monitor für Mauscribe
Überwacht GitHub Actions und zeigt Status-Updates
"""
import time
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import toml

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually read .env file
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        pass

class PipelineMonitor:
    """Überwacht GitHub Actions Pipeline für Mauscribe"""
    
    def __init__(self, config_file: str = ".pipeline-monitor-config"):
        """Initialisiert den Pipeline Monitor"""
        self.config = self._load_config(config_file)
        self.github_token = self._get_github_token()
        
        # Fallback-Werte falls Konfiguration fehlt
        github_config = self.config.get('github', {})
        self.repo_owner = github_config.get('repo_owner', 'R0bes')
        self.repo_name = github_config.get('repo_name', 'Mouscribe')
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
    def _load_config(self, config_file: str) -> Dict:
        """Lädt die Konfiguration aus der TOML-Datei"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except FileNotFoundError:
            print(f"❌ Konfigurationsdatei {config_file} nicht gefunden")
            return {}
        except Exception as e:
            print(f"❌ Fehler beim Laden der Konfiguration: {e}")
            return {}
    
    def _get_github_token(self) -> Optional[str]:
        """Holt GitHub Token aus Umgebungsvariablen"""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️ GITHUB_TOKEN nicht gesetzt. Verwende öffentliche API (limitierte Anfragen)")
        return token
    
    def get_workflow_runs(self, limit: int = 10) -> List[Dict]:
        """Holt die letzten Workflow-Runs"""
        url = f"{self.base_url}/actions/runs"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers, params={'per_page': limit})
            response.raise_for_status()
            data = response.json()
            return data.get('workflow_runs', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abrufen der Workflow-Runs: {e}")
            return []
    
    def get_workflow_status(self, run_id: int) -> Dict:
        """Holt detaillierte Informationen zu einem Workflow-Run"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abrufen des Workflow-Status: {e}")
            return {}
    
    def get_workflow_jobs(self, run_id: int) -> List[Dict]:
        """Holt alle Jobs eines Workflow-Runs"""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('jobs', [])
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abrufen der Workflow-Jobs: {e}")
            return []
    
    def get_job_logs(self, run_id: int, job_id: int) -> str:
        """Holt die Logs eines Jobs"""
        url = f"{self.base_url}/actions/jobs/{job_id}/logs"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abrufen der Job-Logs: {e}")
            return ""
    
    def format_status(self, run: Dict) -> str:
        """Formatiert den Status eines Workflow-Runs"""
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'unknown')
        workflow_name = run.get('name', 'Unknown Workflow')
        created_at = run.get('created_at', '')
        html_url = run.get('html_url', '')
        
        # Status-Icons
        status_icons = {
            'completed': '✅' if conclusion == 'success' else '❌',
            'in_progress': '🔄',
            'queued': '⏳',
            'cancelled': '🚫',
            'failure': '❌',
            'success': '✅'
        }
        
        icon = status_icons.get(status, '❓')
        conclusion_icon = status_icons.get(conclusion, '❓')
        
        # Zeit formatieren
        try:
            if created_at:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
            else:
                time_str = 'Unknown'
        except:
            time_str = 'Unknown'
        
        return f"{icon} {workflow_name} - {status} ({conclusion_icon} {conclusion}) - {time_str} - {html_url}"
    
    def monitor_pipeline(self):
        """Startet das Pipeline-Monitoring"""
        if not self.config.get('monitoring', {}).get('enabled', False):
            print("🔇 Pipeline-Monitoring ist deaktiviert")
            return
        
        max_wait_time = self.config.get('monitoring', {}).get('max_wait_time', 300)
        check_interval = self.config.get('monitoring', {}).get('check_interval', 15)
        
        print(f"🚀 Starte Pipeline-Monitoring für {self.repo_owner}/{self.repo_name}")
        print(f"⏱️ Check-Intervall: {check_interval}s, Max. Wartezeit: {max_wait_time}s")
        print("=" * 80)
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                runs = self.get_workflow_runs(5)
                
                if not runs:
                    print("❌ Keine Workflow-Runs gefunden")
                    time.sleep(check_interval)
                    continue
                
                print(f"\n📊 Pipeline-Status ({datetime.now().strftime('%H:%M:%S')}):")
                print("-" * 60)
                
                for run in runs:
                    status_line = self.format_status(run)
                    print(status_line)
                
                # Prüfe auf laufende Workflows
                running_workflows = [run for run in runs if run.get('status') == 'in_progress']
                if running_workflows:
                    print(f"\n🔄 {len(running_workflows)} Workflow(s) laufen noch...")
                else:
                    print("\n✅ Alle Workflows abgeschlossen")
                
                print("=" * 80)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring durch Benutzer gestoppt")
                break
            except Exception as e:
                print(f"❌ Fehler beim Monitoring: {e}")
            
            time.sleep(check_interval)
        
        print(f"\n⏰ Monitoring nach {max_wait_time}s beendet")
    
    def analyze_failed_runs(self, limit: int = 5):
        """Analysiert die letzten fehlgeschlagenen Runs und zeigt Fehlermeldungen"""
        print(f"🔍 Analysiere die letzten {limit} fehlgeschlagenen Runs...")
        print("=" * 80)
        
        runs = self.get_workflow_runs(limit * 2)  # Hole mehr Runs um fehlgeschlagene zu finden
        failed_runs = [run for run in runs if run.get('conclusion') == 'failure'][:limit]
        
        if not failed_runs:
            print("✅ Keine fehlgeschlagenen Runs gefunden!")
            return
        
        for i, run in enumerate(failed_runs, 1):
            run_id = run.get('id')
            workflow_name = run.get('name', 'Unknown')
            created_at = run.get('created_at', '')
            
            print(f"\n📋 Fehlgeschlagener Run #{i}: {workflow_name}")
            print(f"🆔 Run ID: {run_id}")
            print(f"📅 Erstellt: {created_at}")
            print(f"🔗 URL: {run.get('html_url', 'N/A')}")
            print("-" * 60)
            
            # Hole Jobs für diesen Run
            jobs = self.get_workflow_jobs(run_id)
            
            for job in jobs:
                job_name = job.get('name', 'Unknown Job')
                job_conclusion = job.get('conclusion', 'unknown')
                job_status = job.get('status', 'unknown')
                job_id = job.get('id')
                
                print(f"\n🔧 Job: {job_name}")
                print(f"   Status: {job_status} | Conclusion: {job_conclusion}")
                
                if job_conclusion == 'failure' and job_id:
                    print(f"   📝 Lade Logs für Job {job_id}...")
                    logs = self.get_job_logs(run_id, job_id)
                    
                    if logs:
                        # Zeige die letzten Zeilen der Logs (meist die Fehlermeldung)
                        log_lines = logs.split('\n')
                        error_lines = [line for line in log_lines[-20:] if line.strip()]
                        
                        print(f"   📄 Letzte Log-Zeilen:")
                        for line in error_lines:
                            if 'error' in line.lower() or 'failed' in line.lower() or '❌' in line:
                                print(f"   ❌ {line}")
                            else:
                                print(f"   📝 {line}")
                    else:
                        print("   ⚠️ Keine Logs verfügbar")
            
            print("=" * 80)

def main():
    """Hauptfunktion"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        # Fehlermeldungen analysieren
        monitor = PipelineMonitor()
        monitor.analyze_failed_runs()
    else:
        # Normales Monitoring
        monitor = PipelineMonitor()
        monitor.monitor_pipeline()

if __name__ == "__main__":
    main()
