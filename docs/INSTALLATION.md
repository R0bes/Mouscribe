# Installation Guide

## System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Audio**: Working microphone and speakers

## Quick Installation (Windows)

### Option 1: Automated Installer

1. Download the latest release from GitHub
2. Run `install.bat` as administrator
3. Follow the on-screen instructions
4. Launch with `python main.py`

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mauscribe.git
cd mauscribe

# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Detailed Installation Steps

### 1. Python Installation

Ensure Python 3.8+ is installed:

```bash
python --version
```

If not installed, download from [python.org](https://python.org)

### 2. Repository Setup

```bash
# Clone repository
git clone https://github.com/yourusername/mauscribe.git
cd mauscribe

# Verify structure
dir
```

### 3. Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Verify activation
where python
```

### 4. Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

### 5. Configuration

1. Copy `config.toml.example` to `config.toml`
2. Edit settings as needed
3. Test configuration

## Post-Installation

### First Run

```bash
# Start application
python main.py

# Check system tray icon
# Test microphone access
# Verify volume control
```

### Troubleshooting

#### Common Issues

- **Python not found**: Add Python to PATH
- **Permission denied**: Run as administrator
- **Audio not working**: Check device permissions
- **Import errors**: Verify virtual environment activation

#### Audio Setup

1. **Microphone Access**:
   - Windows Settings → Privacy → Microphone
   - Enable for Mauscribe

2. **Default Device**:
   - Right-click speaker icon → Sound settings
   - Set default input device

3. **Volume Control**:
   - Test system volume
   - Verify microphone levels

### Verification

```bash
# Test components
python -c "import sounddevice; print('Audio OK')"
python -c "import pynput; print('Input OK')"
python -c "import pyperclip; print('Clipboard OK')"
```

## Development Installation

### Additional Tools

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Install testing framework
pip install pytest pytest-cov
```

### IDE Setup

#### VS Code

1. Install Python extension
2. Select Python interpreter (`.venv`)
3. Install recommended extensions

#### PyCharm

1. Open project
2. Configure Python interpreter
3. Set working directory

## Uninstallation

### Remove Application

```bash
# Deactivate virtual environment
deactivate

# Remove directory
rmdir /s mauscribe

# Clean up Python packages (optional)
pip uninstall -r requirements.txt
```

### System Cleanup

1. Remove from startup programs
2. Delete configuration files
3. Clear system tray cache

## Updates

### Automatic Updates

Updates are handled automatically when available.

### Manual Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Rebuild if needed
python build.py
```

## Support

### Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions

### Logs

Enable debug logging in `config.toml`:

```toml
[debug]
enabled = true
level = "DEBUG"
```

Logs are stored in the application directory.
