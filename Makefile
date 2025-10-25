# Mauscribe - Voice-to-Text Tool
# Elegant and functional Makefile for development workflow

.PHONY: help setup install-dev check tests validate fix run clean install-windows install-linux build-exe
.DEFAULT_GOAL := help

# Project configuration
PROJECT_NAME := mauscribe
VENV_DIR := .venv
PYTHON := python
PIP := $(VENV_DIR)/Scripts/pip.exe
PYTHON_VENV := $(VENV_DIR)/Scripts/python.exe

# Detect operating system
ifeq ($(OS),Windows_NT)
    DETECTED_OS := windows
else
    DETECTED_OS := linux
    PYTHON := python3
    PIP := $(VENV_DIR)/bin/pip
    PYTHON_VENV := $(VENV_DIR)/bin/python
endif

# Help target - shows available commands
help: ## Show this help message
	@echo "Mauscribe Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup           Create virtual environment if not present"
	@echo "  install-dev     Install all development dependencies"
	@echo "  install-windows Install Windows-specific dependencies"
	@echo "  install-linux   Install Linux-specific dependencies"
	@echo ""
	@echo "Development:"
	@echo "  check           Run all static code analysis"
	@echo "  tests           Run all dynamic tests"
	@echo "  tests-coverage  Run tests with detailed coverage"
	@echo "  validate        Run complete validation (checks + tests)"
	@echo "  fix             Auto-fix code issues"
	@echo "  run             Run the Mauscribe application"
	@echo "  run-dev         Run application in development mode"
	@echo "  dev             Quick development cycle (fix + check + test)"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  build-exe       Build standalone executable (.exe)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean           Clean up generated files and caches"
	@echo "  status          Show project status and environment info"
	@echo "  help            Show this help message"

# Setup virtual environment
setup: ## Create virtual environment if not present
	@echo "Setting up development environment..."
	@if not exist "$(VENV_DIR)" ( \
		echo "Creating virtual environment..." & \
		$(PYTHON) -m venv $(VENV_DIR) & \
		echo "Virtual environment created" \
	) else ( \
		echo "Virtual environment already exists" \
	)
	@echo "Detected OS: $(DETECTED_OS)"

# Install development dependencies
install-dev: setup ## Install all development dependencies
	@echo "Installing dependencies for $(DETECTED_OS)..."
	@$(PYTHON_VENV) -m pip install --upgrade pip
	@$(PIP) install -e .
	@if "$(DETECTED_OS)"=="windows" ( \
		echo "Installing Windows-specific packages..." & \
		$(PIP) install -e ".[windows]" \
	) else ( \
		echo "Installing Linux-specific packages..." & \
		$(PIP) install -e ".[linux]" \
	)
	@$(PIP) install -e ".[dev]"
	@echo "All dependencies installed successfully"

# Install Windows-specific dependencies
install-windows: setup ## Install Windows-specific dependencies
	@echo "Installing Windows-specific packages..."
	@$(PIP) install -e ".[windows]"
	@echo "Windows dependencies installed"

# Install Linux-specific dependencies
install-linux: setup ## Install Linux-specific dependencies
	@echo "Installing Linux-specific packages..."
	@$(PIP) install -e ".[linux]"
	@echo "Linux dependencies installed"

# Run static code analysis and checks
check: ## Run all static code analysis (linting, type checking, formatting)
	@echo "Running static code analysis..."
	@echo "Running Black formatter check..."
	@$(PYTHON_VENV) -m black --check --diff src/ main.py
	@echo "Running isort import sorting check..."
	@$(PYTHON_VENV) -m isort --check-only --diff src/ main.py
	@echo "Running Flake8 linting..."
	@$(PYTHON_VENV) -m flake8 src/ main.py
	@echo "Running MyPy type checking..."
	@$(PYTHON_VENV) -m mypy src/ main.py
	@echo "Running pre-commit hooks..."
	@$(PYTHON_VENV) -m pre_commit run --all-files
	@echo "All static checks passed"

# Run all tests
tests: ## Run all dynamic tests
	@echo "Running test suite..."
	@$(PYTHON_VENV) -m pytest tests/ -v --tb=short --cov=src --cov-report=html --cov-report=term-missing
	@echo "All tests completed"

# Run tests with coverage report
tests-coverage: ## Run tests with detailed coverage report
	@echo "Running tests with coverage..."
	@$(PYTHON_VENV) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/index.html"

# Validate everything (checks + tests)
validate: check tests ## Run complete validation (checks + tests)
	@echo "All validations passed!"

# Auto-fix code issues where possible
fix: ## Auto-fix code issues (formatting, imports, etc.)
	@echo "Auto-fixing code issues..."
	@echo "Running Black formatter..."
	@$(PYTHON_VENV) -m black src/ main.py
	@echo "Running isort import sorting..."
	@$(PYTHON_VENV) -m isort src/ main.py
	@echo "Running pre-commit auto-fix..."
	@$(PYTHON_VENV) -m pre_commit run --all-files
	@echo "Auto-fix completed"

# Run the application
run: ## Run the Mauscribe application
	@echo "Starting Mauscribe..."
	@$(PYTHON_VENV) python main.py

# Run application in development mode
run-dev: ## Run application in development mode with debug output
	@echo "Starting Mauscribe in development mode..."
	@set DEBUG=1 && $(PYTHON_VENV) python main.py

# Clean up generated files
clean: ## Clean up generated files and caches
	@echo "Cleaning up..."
	@if exist "__pycache__" rmdir /s /q __pycache__
	@if exist "src\__pycache__" rmdir /s /q src\__pycache__
	@if exist "build" rmdir /s /q build
	@if exist "dist" rmdir /s /q dist
	@if exist ".coverage" del .coverage
	@if exist "htmlcov" rmdir /s /q htmlcov
	@if exist ".pytest_cache" rmdir /s /q .pytest_cache
	@if exist ".mypy_cache" rmdir /s /q .mypy_cache
	@if exist "$(VENV_DIR)" rmdir /s /q $(VENV_DIR)
	@echo "Cleanup completed"

# Quick development cycle
dev: fix check tests ## Quick development cycle (fix + check + test)
	@echo "Development cycle completed!"

# Build standalone executable
build-exe: ## Build standalone executable (.exe)
	@echo "Building Mauscribe executable..."
	@echo "Stopping any running instances..."
	@taskkill /F /IM Mauscribe.exe 2>nul || echo "No running instances found"
	@echo "Cleaning previous build..."
	@if exist "build" rmdir /s /q build
	@if exist "dist" rmdir /s /q dist
	@echo "Building with PyInstaller..."
	@$(PYTHON_VENV) -m PyInstaller mauscribe.spec --clean
	@echo "Build completed!"
	@if exist "dist\Mauscribe.exe" ( \
		echo "✅ Executable created: dist\Mauscribe.exe" & \
		for %%A in ("dist\Mauscribe.exe") do echo "   Size: %%~zA bytes" \
	) else ( \
		echo "❌ Build failed - executable not found" & \
		exit /b 1 \
	)

# Show project status
status: ## Show project status and environment info
	@echo "Mauscribe Project Status"
	@echo "========================"
	@echo "OS: $(DETECTED_OS)"
	@echo "Python: $(PYTHON)"
	@echo "Virtual Env: $(if exist '$(VENV_DIR)',Present,Missing)"
	@echo "Dependencies: $(if exist '$(VENV_DIR)/pyvenv.cfg',Installed,Not installed)"
	@echo "Project Files: Available"

# Release management targets
release-patch: ## Bump patch version and create release
	@echo "Creating patch release..."
	@$(PYTHON_VENV) python tools/version_bump.py patch

release-minor: ## Bump minor version and create release
	@echo "Creating minor release..."
	@$(PYTHON_VENV) python tools/version_bump.py minor

release-major: ## Bump major version and create release
	@echo "Creating major release..."
	@$(PYTHON_VENV) python tools/version_bump.py major

changelog: ## Generate changelog preview
	@echo "Generating changelog preview..."
	@$(PYTHON_VENV) python -c "from tools.release_manager import ReleaseManager; rm = ReleaseManager(); latest = rm.get_latest_tag(); print('Latest tag:', latest); print('Changelog:'); print(rm.generate_changelog(latest) if latest else 'No previous tag found')"

upload-release: ## Upload release artifacts to GitHub
	@echo "Uploading release artifacts..."
	@$(PYTHON_VENV) python tools/release_manager.py --tag $(shell git describe --tags --abbrev=0) --upload

# Development release (for testing)
dev-release: ## Create development release with current changes
	@echo "Creating development release..."
	@$(PYTHON_VENV) python tools/version_bump.py patch
