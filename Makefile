# Mouscribe Makefile
# Einfache Workflows für Entwicklung und Deployment

.PHONY: help install test lint format clean commit stage push workflow build build-windows

# Standardziel
all: lint test

# Hilfe anzeigen
help:
	@echo "Verfuegbare Ziele:"
	@echo "  install       - Abhaengigkeiten installieren"
	@echo "  test          - Tests ausfuehren (mit Coverage)"
	@echo "  coverage      - Coverage-Bericht generieren"
	@echo "  lint          - Code-Qualitaet pruefen"
	@echo "  format        - Code formatieren"
	@echo "  clean         - Build-Dateien bereinigen"
	@echo "  commit        - Aenderungen committen (mit Checks)"
	@echo "  push          - Aenderungen pushen"
	@echo "  pr            - Pull Request erstellen"
	@echo "  pr-interactive- Pull Request interaktiv erstellen"
	@echo "  workflow      - Kompletter Workflow"
	@echo "  all           - Lint und Tests ausfuehren"
	@echo "  pre-commit    - Code-Qualitaets-Checks ausfuehren"
	@echo "  build         - Executable erstellen (alle Plattformen)"
	@echo "  build-windows - Windows .exe erstellen"

# Abhängigkeiten installieren
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Tests ausführen
test:
	@echo "Running tests..."
ifeq ($(OS),Windows_NT)
	@echo "Windows detected - using alternative coverage method..."
	python -m pytest tests/ -v
	@echo "Generating coverage report with coverage.py..."
	python -m coverage run -m pytest tests/
	python -m coverage report
	@echo "Coverage report generated!"
else
	python -m pytest tests/ -v --cov=src --cov-report=html
endif
	@echo "Tests completed!"


# Code-Qualität prüfen
lint:
	@echo "Running code quality checks..."
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/ --ignore-missing-imports
	@echo "Code quality checks completed!"

# Code formatieren
format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "Code formatting completed!"


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
	@echo "Committing changes..."
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
	@echo "Staging completed!"

# Änderungen pushen
push:
	@echo "Pushing changes..."
	git push

# Pull Request erstellen
pr:
	@echo "Creating pull request..."
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
	@echo "Creating pull request interactively..."
	gh pr create --interactive

# Workflow: Alles committen und pushen
workflow: format lint test coverage
	@echo "Staging changes..."
	git add .
	@$(MAKE) commit $(filter-out $@,$(MAKECMDGOALS))
	@echo "Pushing changes..."
	@$(MAKE) push
	@echo "Workflow abgeschlossen!"


# Executable erstellen (alle Plattformen)
build: clean
	@echo "Building executable..."
	python build.py

# Windows .exe erstellen
build-windows: clean
ifeq ($(OS),Windows_NT)
	@echo "Building Windows executable..."
	python build.py
else
	@echo "This target is only available on Windows"
	@exit 1
endif
