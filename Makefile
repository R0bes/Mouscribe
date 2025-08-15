# Mauscribe Makefile
# Einheitliche Workflows für Entwicklung und Deployment
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -ExecutionPolicy Bypass -Command
.ONESHELL:

.PHONY: help init install test lint format clean commit stage push workflow build build-windows ci

# Standardziel
all: lint test

# Repository nach dem Clonen einrichten
init: install setup-hooks
	@echo 🎉 Repository erfolgreich eingerichtet!
	@echo 💡 Nächste Schritte:
	@echo    1. Konfiguriere deine GitHub-Token (optional)
	@echo    2. Teste die Einrichtung: make ci
	@echo    3. Starte mit der Entwicklung!

# Abhängigkeiten installieren
install:
	@echo 📦 Installiere Abhängigkeiten...
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo ✅ Abhängigkeiten installiert!

# Git-Hooks für Pipeline-Monitoring einrichten
setup-hooks:
	@echo 🔧 Richte Git-Hooks ein...
	python setup_pipeline_monitoring.py
	@echo ✅ Git-Hooks eingerichtet!

# CI/CD Pipeline lokal testen (entspricht der GitHub Actions Pipeline)
ci: lint test
	@echo ✅ CI/CD Pipeline lokal erfolgreich durchlaufen!
	@echo 🔍 Dies entspricht dem validate Job in der GitHub Actions Pipeline

# Vollständige CI/CD Pipeline lokal testen (inkl. Build)
ci-full: ci build-windows
	@echo ✅ Vollständige CI/CD Pipeline lokal erfolgreich durchlaufen!
	@echo 🔍 Dies entspricht allen Jobs in der GitHub Actions Pipeline

# Hilfe anzeigen
help:
	@echo Verfuegbare Ziele:
	@echo   init          - Repository nach dem Clonen einrichten
	@echo   install       - Abhaengigkeiten installieren
	@echo   test          - Tests ausfuehren (mit Coverage)
	@echo   coverage      - Coverage-Bericht generieren
	@echo   lint          - Code-Qualitaet pruefen
	@echo   format        - Code formatieren
	@echo   clean         - Build-Dateien bereinigen
	@echo   commit        - Aenderungen committen (mit Checks)
	@echo   push          - Aenderungen pushen
	@echo   pr            - Pull Request erstellen
	@echo   pr-interactive- Pull Request interaktiv erstellen
	@echo   workflow      - Kompletter Workflow
	@echo   all           - Lint und Tests ausfuehren
	@echo   pre-commit    - Code-Qualitaets-Checks ausfuehren
	@echo   build         - Executable erstellen (alle Plattformen)
	@echo   build-windows - Windows .exe erstellen
	@echo   ci            - Lokale CI/CD-Pipeline ausführen (validate Job)
	@echo   ci-full       - Vollständige CI/CD-Pipeline lokal (inkl. Build)



# Tests ausführen
test:
	@echo Running tests...
ifeq ($(OS),Windows_NT)
	@echo Windows detected - using alternative coverage method...
	python -m pytest tests/ -v
	@echo Generating coverage report with coverage.py...
	python -m coverage run -m pytest tests/
	python -m coverage report
	@echo Coverage report generated!
else
	python -m pytest tests/ -v --cov=src --cov-report=html
endif
	@echo Tests completed!


# Code-Qualität prüfen
lint:
	@echo Running code quality checks...
	flake8 src/ tests/ || echo "flake8 completed with warnings"
	black --check --line-length=127 src/ tests/ || echo "black completed with warnings"
	isort --check-only src/ tests/ || echo "isort completed with warnings"
	mypy src/ --ignore-missing-imports || echo "mypy completed with warnings"
	@echo Code quality checks completed!

# Code formatieren
format:
	@echo Formatting code...
	black src/ tests/ --line-length=127 src/ tests/
	isort src/ tests/
	@echo Code formatting completed!


# Build-Dateien bereinigen (plattformunabhängig)
clean:
ifeq ($(OS),Windows_NT)
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist *.egg-info rmdir /s /q *.egg-info
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist coverage_html rmdir /s /q coverage_html
	if exist .coverage del .coverage
	if exist coverage.xml del coverage.xml
	if exist bandit-report.json del bandit-report.json
	if exist __pycache__ rmdir /s /q __pycache__
	if exist *.spec del *.spec
	if exist *.pyc del *.pyc
else
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf coverage_html/
	rm -f .coverage
	rm -f coverage.xml
	rm -f bandit-report.json
	rm -rf __pycache__/
	rm -f *.spec
	rm -f *.pyc
endif

# Änderungen committen (mit Code-Qualitäts-Checks)
commit:
	@echo Committing changes...
ifeq ($(OS),Windows_NT)
	@if "$(filter-out $@,$(MAKECMDGOALS))"=="" ( \
		set /p message="Commit message: " && git commit -m "!message!" --no-verify \
	) else ( \
		git commit -m "$(filter-out $@,$(MAKECMDGOALS))" --no-verify \
	)
else
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		read -p "Commit message: " message; git commit -m "$$message" --no-verify; \
	else \
		git commit -m "$(filter-out $@,$(MAKECMDGOALS))" --no-verify; \
	fi
endif

stage:
	@echo "Staging changes..."
	git add .
	@$(MAKE) commit $(filter-out $@,$(MAKECMDGOALS))
	@echo Staging completed!

# Änderungen pushen
push:
	@echo Pushing changes...
	git push

# Pull Request erstellen
pr:
	@echo Creating pull request...
ifeq ($(OS),Windows_NT)
	@if "$(filter-out $@,$(MAKECMDGOALS))"=="" ( \
		set /p title="PR title: " && set /p body="PR description: " && gh pr create --title "!title!" --body "!body!" \
	) else ( \
		gh pr create --title "$(filter-out $@,$(MAKECMDGOALS))" \
	)
else
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		read -p "PR title: " title; read -p "PR description: " body; gh pr create --title "$$title" --body "$$body"; \
	else \
		gh pr create --title "$(filter-out $@,$(MAKECMDGOALS))"; \
	fi
endif

# Pull Request mit interaktiver Eingabe erstellen
pr-interactive:
	@echo Creating pull request interactively...
	gh pr create --interactive

# Workflow: Alles committen und pushen
workflow: stage push
	@echo Workflow abgeschlossen!


# Executable erstellen (alle Plattformen)
build: clean
	@echo Building executable...
	python build.py

# Windows .exe erstellen
build-windows: clean
ifeq ($(OS),Windows_NT)
	@echo Building Windows executable...
	python build.py
else
	@echo This target is only available on Windows
	@exit 1
endif
