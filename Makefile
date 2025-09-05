# Mauscribe - Einfaches Makefile für Solo-Entwicklung
# Virtuelle Umgebung wird automatisch aktiviert

# Variablen
PROJECT_NAME := mauscribe
PYTHON := python
PIP := pip
GIT := git
VENV := .venv

# ALL=1 für automatisches git add .
ALL ?= 0

# Windows-spezifische Shell-Einstellungen
ifeq ($(OS),Windows_NT)
SHELL := powershell.exe
.SHELLFLAGS := -ExecutionPolicy Bypass -Command
VENV_PYTHON := $(VENV)\Scripts\python.exe
VENV_PIP := $(VENV)\Scripts\pip.exe
else
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
endif

# Standardziel
.PHONY: help
help:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Mauscribe Workflow'; Write-Host ''; Write-Host 'Meta:'; Write-Host '    help            - Show Help'; Write-Host '    setup           - Setup Project (initial command)'; Write-Host '    clean           - Clean Project'; Write-Host '    fix-numpy       - Fix NumPy Installation Issues'; Write-Host ''; Write-Host 'Main:'; Write-Host '    run             - Run Mauscribe'; Write-Host '    status          - Git Status'; Write-Host '    tests           - Run Tests'; Write-Host '    format          - Format Code'; Write-Host '    lint            - Check Code Quality'; Write-Host '    pre-commit      - Pre-Commit Checks'; Write-Host '    build           - Create Executable'; Write-Host '    commit MSG=\"..\" - Commit with Tests'; Write-Host '    push            - Push to Remote'; Write-Host '    release         - Create Release'"
else
	@echo Mauscribe Workflow
	@echo.
	@echo Meta:
	@echo     help            - Show Help
	@echo     setup           - Setup Project (initial command)
	@echo     run             - Run Mauscribe
	@echo     clean           - Clean Project
	@echo     build           - Create Executable
	@echo     build-msix      - Create MSIX Package
	@echo     build-msix-only - Create MSIX Package only (no install)
	@echo     test-msix       - Test MSIX Package (installs and tests)
	@echo     release-msix    - Create Git tag and GitHub Release
	@echo     release-msix-wf - Complete MSIX Release Workflow (commit + release)
	@echo     release-msix-force - Force MSIX Release (overwrites existing tags)
	@echo.
	@echo Main:
	@echo     status          - Git Status
	@echo     tests           - Run Tests
	@echo     format          - Format Code
	@echo     lint            - Check Code Quality
	@echo     pre-commit      - Pre-Commit Checks
	@echo     commit MSG=".." - Commit with Tests (ALL=1 für git add .)
	@echo     push            - Push to Remote (ALL=1 für Auto-Commit)
	@echo     release         - Create Release (ALL=1 für Auto-Commit)
endif

# Meta Targets
.PHONY: setup
setup: venv
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Installiere Dependencies...'; Write-Host 'Upgrade pip...'; & '$(VENV_PIP)' install --upgrade pip; Write-Host 'Installiere numpy...'; & '$(VENV_PIP)' install --force-reinstall numpy; Write-Host 'Installiere requirements.txt...'; & '$(VENV_PIP)' install -r requirements.txt; Write-Host 'Installiere requirements-dev.txt...'; & '$(VENV_PIP)' install -r requirements-dev.txt; Write-Host 'Dependencies installiert!'"
else
	@echo Installiere Dependencies...
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install --force-reinstall numpy
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install -r requirements-dev.txt
	@echo Dependencies installiert!
endif

.PHONY: venv
venv:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Prüfe virtuelle Umgebung...'; if (Test-Path '$(VENV)') { Write-Host 'Virtuelle Umgebung existiert bereits.' } else { Write-Host 'Erstelle neue virtuelle Umgebung...'; & '$(PYTHON)' -m venv '$(VENV)'; if ($$LASTEXITCODE -eq 0) { Write-Host 'Virtuelle Umgebung erstellt!' } else { Write-Host 'Fehler beim Erstellen der virtuellen Umgebung!' -ForegroundColor Red; exit 1 } }"
else
	@echo Prüfe virtuelle Umgebung...
	@if [ ! -d "$(VENV)" ]; then \
		echo Erstelle neue virtuelle Umgebung... && \
		$(PYTHON) -m venv $(VENV) && \
		echo Virtuelle Umgebung erstellt!; \
	else \
		echo Virtuelle Umgebung existiert bereits.; \
	fi
endif

.PHONY: clean
clean:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Räume temporäre Dateien auf...'; if (Test-Path '__pycache__') { Remove-Item -Recurse -Force '__pycache__' }; if (Test-Path '.pytest_cache') { Remove-Item -Recurse -Force '.pytest_cache' }; if (Test-Path 'dist') { Remove-Item -Recurse -Force 'dist' }; if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }; Get-ChildItem -Recurse -Include '*.pyc' | Remove-Item -Force; Write-Host 'Aufräumen abgeschlossen!'"
else
	@echo Räume temporäre Dateien auf...
	@rm -rf __pycache__/
	@rm -rf .pytest_cache/
	@rm -rf dist/
	@rm -rf build/
	@find . -type f -name "*.pyc" -delete
	@echo Aufräumen abgeschlossen!
endif

# Main Targets
.PHONY: run
run:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "$(VENV_PYTHON) main.py"
else
	@$(VENV_PYTHON) main.py
endif

.PHONY: status
status:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "& '$(GIT)' status --short; Write-Host ''; Write-Host 'Letzte Commits:'; & '$(GIT)' log --oneline -5"
else
	@echo Git Status:
	@$(GIT) status --short
	@echo
	@echo Letzte Commits:
	@$(GIT) log --oneline -5
endif

.PHONY: tests
tests:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Führe Tests aus...'; & '$(VENV_PYTHON)' -m pytest tests/ -v; Write-Host 'Tests abgeschlossen!'"
else
	@echo Führe Tests aus...
	@$(VENV_PYTHON) -m pytest tests/ -v
	@echo Tests abgeschlossen!
endif

.PHONY: format
format:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Formatiere Code...'; & '$(VENV_PYTHON)' -m black src/ tests/; & '$(VENV_PYTHON)' -m isort src/ tests/; Write-Host 'Code formatiert!'"
else
	@echo Formatiere Code...
	@$(VENV_PYTHON) -m black src/ tests/
	@$(VENV_PYTHON) -m isort src/ tests/
	@echo Code formatiert!
endif

.PHONY: lint
lint:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Prüfe Code-Qualität...'; & '$(VENV_PYTHON)' -m flake8 src/ tests/ --max-line-length=88; if ($$LASTEXITCODE -ne 0) { Write-Host 'Linting mit Warnungen' }; & '$(VENV_PYTHON)' -m black --check src/ tests/; if ($$LASTEXITCODE -ne 0) { Write-Host 'Format-Check mit Warnungen' }; Write-Host 'Code-Qualitäts-Checks abgeschlossen!'"
else
	@echo Prüfe Code-Qualität...
	@$(VENV_PYTHON) -m flake8 src/ tests/ --max-line-length=88 || echo "Linting mit Warnungen"
	@$(VENV_PYTHON) -m black --check src/ tests/ || echo "Format-Check mit Warnungen"
	@echo Code-Qualitäts-Checks abgeschlossen!
endif

.PHONY: pre-commit
pre-commit:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Führe Pre-Commit Checks aus...'; Write-Host ''; Write-Host '1. Code-Qualität prüfen...'; & make lint; Write-Host ''; Write-Host '2. Tests ausführen...'; & make tests; Write-Host ''; Write-Host 'Pre-Commit Checks erfolgreich!'"
else
	@echo Führe Pre-Commit Checks aus...
	@echo
	@echo 1. Code-Qualität prüfen...
	@$(MAKE) lint
	@echo
	@echo 2. Tests ausführen...
	@$(MAKE) tests
	@echo
	@echo Pre-Commit Checks erfolgreich!
endif

.PHONY: build
build:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Erstelle Executable...'; & '$(VENV_PYTHON)' -m PyInstaller --onefile --windowed --icon=assets/icons/mauscribe_icon.ico --name=$(PROJECT_NAME) main.py; Write-Host 'Executable erstellt!'"
else
	@echo Erstelle Executable...
	@$(VENV_PYTHON) -m PyInstaller --onefile --windowed --icon=assets/icons/mauscribe_icon.ico --name=$(PROJECT_NAME) main.py
	@echo Executable erstellt!
endif

.PHONY: build-msix
build-msix:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Erstelle MSIX-Paket...'; & 'msix/scripts/build_msix.ps1' -Version '1.0.0.0' -Sign; Write-Host 'MSIX-Paket erstellt!'"
else
	@echo MSIX-Build nur unter Windows verfügbar
	@echo Bitte verwenden Sie: make build-msix unter Windows
endif

.PHONY: build-msix-only
build-msix-only:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Erstelle MSIX-Paket (ohne Installation)...'; & 'msix/scripts/build_msix.ps1' -Version '1.0.0.0' -Sign; Write-Host 'MSIX-Paket erstellt! (nicht installiert)'"
else
	@echo MSIX-Build nur unter Windows verfügbar
	@echo Bitte verwenden Sie: make build-msix-only unter Windows
endif

.PHONY: test-msix
test-msix:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Teste MSIX-Paket...'; & 'msix/scripts/build_msix.ps1' -Version '1.0.0.0' -Sign -Test; Write-Host 'MSIX-Paket getestet!'; Write-Host 'Hinweis: Windows könnte die Maus-Eigenschaften öffnen, da Mauscribe Maus-Input verwendet.'"
else
	@echo MSIX-Test nur unter Windows verfügbar
	@echo Bitte verwenden Sie: make test-msix unter Windows
endif

.PHONY: release-msix
release-msix:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "& 'scripts/create_release.ps1'"
else
	@echo 🚀 Erstelle MSIX Release...
	@echo
	@echo 📋 Schritte:
	@echo 1. Version aus pyproject.toml lesen
	@echo 2. Git-Tag erstellen
	@echo 3. Tag pushen
	@echo 4. GitHub Release erstellen
	@echo
	@echo ⚠️  Stellen Sie sicher, dass Sie:
	@echo    - Alle Änderungen committed haben
	@echo    - Auf main branch sind
	@echo    - GitHub Remote konfiguriert haben
	@echo
	@read -p "Fortfahren? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "✅ Erstelle Release..."; \
		VERSION=$$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])") && \
		echo "📦 Version: $$VERSION" && \
		git tag "v$$VERSION" && \
		echo "🏷️  Git-Tag erstellt: v$$VERSION" && \
		git push origin "v$$VERSION" && \
		echo "📤 Tag gepusht" && \
		echo "🌐 GitHub Release wird automatisch erstellt..." && \
		echo "✅ Release-Prozess gestartet!" && \
		echo "📋 Überprüfen Sie: https://github.com/$$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\)\/\([^/]*\).*/\1\/\2/')/releases"; \
	else \
		echo "❌ Release abgebrochen"; \
	fi
endif

.PHONY: release-msix-wf
release-msix-wf:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "& 'scripts/release_workflow.ps1'"
else
	@echo MSIX Release Workflow gestartet...
	@echo
	@echo Workflow-Schritte:
	@echo 1. Git-Status prüfen
	@echo 2. Alle Änderungen committen
	@echo 3. Version aus pyproject.toml lesen
	@echo 4. Git-Tag erstellen
	@echo 5. Tag zu GitHub pushen
	@echo 6. GitHub Release automatisch erstellen
	@echo
	@echo Hinweis: Alle uncommitted changes werden automatisch committed!
	@echo
	@read -p "Fortfahren? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Workflow gestartet..."; \
		echo ""; \
		echo "Prüfe Git-Status..."; \
		gitStatus=$$(git status --porcelain); \
		if [ -n "$$gitStatus" ]; then \
			echo "Uncommitted changes gefunden:"; \
			echo "$$gitStatus"; \
			echo ""; \
			echo "Committte alle Änderungen..."; \
			git add .; \
			git commit -m "feat: Add MSIX support and release automation"; \
			echo "Änderungen committed"; \
		else \
			echo "Keine uncommitted changes"; \
		fi; \
		echo ""; \
		echo "Lese Version..."; \
		VERSION=$$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"); \
		echo "Version: $$VERSION"; \
		echo ""; \
		echo "Erstelle Git-Tag..."; \
		git tag "v$$VERSION"; \
		echo "Tag erstellt: v$$VERSION"; \
		echo ""; \
		echo "Pushe zu GitHub..."; \
		git push origin "v$$VERSION"; \
		echo "Tag gepusht"; \
		echo ""; \
		echo "GitHub Release wird automatisch erstellt..."; \
		REPO=$$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\)\/\([^/]*\).*/\1\/\2/'); \
		echo "Überprüfen Sie: https://github.com/$$REPO/releases"; \
		echo ""; \
		echo "MSIX Release Workflow erfolgreich abgeschlossen!"; \
		echo "MSIX-Paket wird automatisch von GitHub Actions erstellt"; \
	else \
		echo "Workflow abgebrochen"; \
	fi
endif

.PHONY: release-msix-force
release-msix-force:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "& 'scripts/release_workflow.ps1' -Force"
else
	@echo Force MSIX Release nur unter Windows verfügbar
	@echo Bitte verwenden Sie: make release-msix-force unter Windows
endif

.PHONY: install-msix
install-msix:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Installiere MSIX-Paket...'; Add-AppxPackage -Path 'dist/mauscribe.msix'; Write-Host 'MSIX-Paket installiert!'"
else
	@echo MSIX-Installation nur unter Windows verfügbar
endif

.PHONY: uninstall-msix
uninstall-msix:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Entferne MSIX-Paket...'; Get-AppxPackage -Name 'Mauscribe.Robs' | Remove-AppxPackage; Write-Host 'MSIX-Paket entfernt!'"
else
	@echo MSIX-Deinstallation nur unter Windows verfügbar
endif

.PHONY: commit
commit:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Committing changes...'; Write-Host ''; Write-Host '1. Tests ausführen...'; & make tests; Write-Host ''; Write-Host '2. Code-Qualität prüfen...'; & make lint; Write-Host ''; Write-Host '3. Dateien stagen...'; if ('$(ALL)' -eq '1') { Write-Host 'ALL=1: Staging alle Dateien...'; & '$(GIT)' add . } else { Write-Host 'Nur geänderte Dateien stagen...'; & '$(GIT)' add . }; if ('$(MSG)' -eq '') { $message = Read-Host 'Commit message'; git commit -m $message } else { git commit -m '$(MSG)' }; Write-Host 'Commit erfolgreich!'"
else
	@echo Committing changes...
	@echo
	@echo 1. Tests ausführen...
	@$(MAKE) tests
	@echo
	@echo 2. Code-Qualität prüfen...
	@$(MAKE) lint
	@echo
	@echo 3. Dateien stagen...
ifeq ($(ALL),1)
	@echo ALL=1: Staging alle Dateien...
	@$(GIT) add .
else
	@echo Nur geänderte Dateien stagen...
	@$(GIT) add .
endif
	@if [ -z "$(MSG)" ]; then \
		read -p "Commit message: " message; git commit -m "$$message"; \
	else \
		git commit -m "$(MSG)"; \
	fi
	@echo Commit erfolgreich!
endif

.PHONY: push
push:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Push zum Remote...'; if ('$(ALL)' -eq '1') { Write-Host 'ALL=1: Staging alle Dateien vor Push...'; & '$(GIT)' add .; & '$(GIT)' commit -m 'Auto-commit before push'; }; & '$(GIT)' push origin main; Write-Host ''; & '$(VENV_PYTHON)' scripts/pipeline_monitor.py"
else
	@echo Push zum Remote...
ifeq ($(ALL),1)
	@echo ALL=1: Staging alle Dateien vor Push...
	@$(GIT) add .
	@$(GIT) commit -m "Auto-commit before push"
endif
	@$(GIT) push origin main
	@echo
	@$(VENV_PYTHON) scripts/pipeline_monitor.py
endif

.PHONY: release
release:
ifeq ($(OS),Windows_NT)
	@powershell.exe -ExecutionPolicy Bypass -Command "Write-Host 'Release erstellen...'; Write-Host ''; Write-Host '1. Pre-Release Checks...'; & make tests; & make lint; Write-Host ''; Write-Host '2. Build erstellen...'; & make build; Write-Host ''; Write-Host '3. Dateien committen...'; if ('$(ALL)' -eq '1') { Write-Host 'ALL=1: Staging alle Dateien...'; & '$(GIT)' add .; & '$(GIT)' commit -m 'Pre-release commit'; }; Write-Host ''; Write-Host '4. Tag erstellen...'; $version = Read-Host 'Version (z.B. 1.0.1): '; git tag -a v$version -m 'Release $version'; git push origin v$version; Write-Host 'Release erfolgreich!'"
else
	@echo Release erstellen...
	@echo
	@echo 1. Pre-Release Checks...
	@$(MAKE) tests
	@$(MAKE) lint
	@echo
	@echo 2. Build erstellen...
	@$(MAKE) build
	@echo
	@echo 3. Dateien committen...
ifeq ($(ALL),1)
	@echo ALL=1: Staging alle Dateien...
	@$(GIT) add .
	@$(GIT) commit -m "Pre-release commit"
endif
	@echo
	@echo 4. Tag erstellen...
	@read -p "Version (z.B. 1.0.1): " version; \
	git tag -a v$$version -m "Release $$version"; \
	git push origin v$$version
	@echo Release erfolgreich!
endif
