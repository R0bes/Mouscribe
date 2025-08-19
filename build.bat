@echo off
echo Mauscribe Windows Build Script
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo Running tests...
python -m pytest tests/ -v
if errorlevel 1 (
    echo Tests failed! Build aborted.
    pause
    exit /b 1
)

echo Running linting...
flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
if errorlevel 1 (
    echo Linting failed! Build aborted.
    pause
    exit /b 1
)

echo Building executable...
python build.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable location: dist\mauscribe.exe
pause
