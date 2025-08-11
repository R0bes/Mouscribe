# Mouscribe Makefile
# Einfache Workflows für Entwicklung und Deployment

.PHONY: help install test lint format clean commit push all workflow pre-commit

# Standardziel
all: lint test

# Hilfe anzeigen
help:
	@echo "Verfuegbare Ziele:"
	@echo "  install    - Abhaengigkeiten installieren"
	@echo "  test       - Tests ausfuehren"
	@echo "  lint       - Code-Qualitaet pruefen"
	@echo "  format     - Code formatieren"
	@echo "  clean      - Build-Dateien bereinigen"
	@echo "  commit     - Aenderungen committen (mit Checks)"
	@echo "  push       - Aenderungen pushen"
	@echo "  workflow   - Kompletter Workflow"
	@echo "  all        - Lint und Tests ausfuehren"
	@echo "  pre-commit - Code-Qualitaets-Checks ausfuehren"

# Abhängigkeiten installieren
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Tests ausführen
test:
	python -m pytest tests/ -v --cov=src --cov-report=html

# Code-Qualität prüfen
lint:
	@echo "Running code quality checks..."
	flake8 src/ tests/
	mypy src/
	bandit -r src/
	@echo "Code quality checks completed!"

# Code formatieren
format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "Code formatting completed!"

# Pre-commit Checks ausführen
pre-commit:
	@echo "Running pre-commit checks..."
ifeq ($(OS),Windows_NT)
	python -m pre_commit run --all-files
else
	pre-commit run --all-files
endif
	@echo "Pre-commit checks completed!"

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
endif

# Änderungen committen (mit Code-Qualitäts-Checks)
commit: pre-commit
	@echo "Committing changes..."
ifeq ($(OS),Windows_NT)
	@set /p message="Commit message: " && git add . && git commit -m "!message!"
else
	@read -p "Commit message: " message; git add . && git commit -m "$$message"
endif

# Änderungen pushen
push:
	@echo "Pushing changes..."
	git push origin feature/custom-dictionary

# Workflow: Alles committen und pushen
workflow: format lint test commit push
	@echo "Workflow abgeschlossen!"
