# Mauscribe - Voice-to-Text Tool

A powerful voice-to-text tool designed for efficient text input and multi-agent AI workflows.

## Features

- **Voice Recording**: High-quality audio recording with automatic volume management
- **Speech-to-Text**: Fast and accurate transcription using Whisper
- **Smart Input**: Mouse button and keyboard shortcuts for intuitive control
- **System Tray**: Background operation with easy access
- **Multi-Agent Support**: Perfect for managing multiple AI agents simultaneously

## Perfect Workflow for AI Agents

Mauscribe is specifically designed for users working with multiple AI agents simultaneously. Instead of manually typing in different chat windows, simply:

1. **Record your message** using the mouse button or keyboard shortcut
2. **Paste automatically** into any AI agent window with a double-click
3. **Switch between agents** seamlessly without losing your workflow

### Practical Use Cases

- **Multiple ChatGPT instances**: Manage conversations across different topics
- **Various AI tools**: Use with Claude, Bard, or other AI assistants
- **Efficient workflows**: Save time by speaking instead of typing
- **Parallel processing**: Work with multiple AI agents simultaneously

## Installation

### Windows
```bash
# Clone the repository
git clone https://github.com/yourusername/mauscribe.git
cd mauscribe

# Run the installer
install.bat
```

### Manual Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Configure settings** in `config.toml`

3. **Use mouse button** (X2) or keyboard shortcut to start recording

4. **Double-click** to paste transcribed text

## Configuration

Edit `config.toml` to customize:
- Input methods (mouse button, keyboard)
- Audio settings
- Speech-to-text parameters
- System behavior

## Development

### Project Structure
```
mauscribe/
├── src/                    # Core application code
├── docs/                   # Documentation
├── icons/                  # Application icons
├── config.toml            # Configuration file
├── requirements.txt       # Dependencies
├── build.py              # Build script
└── main.py               # Entry point
```

### Building
```bash
python build.py
```

### Testing
```bash
# Run all tests with coverage
python run_tests.py

# Or run tests manually
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_config.py -v
```

### Code Quality
```bash
# Install pre-commit hooks
pre-commit install

# Run all checks manually
pre-commit run --all-files

# Format code
black src/
isort src/
```

### Pipeline Monitoring
```bash
# Set up automated pipeline monitoring
python setup_pipeline_monitoring.py

# Monitor pipelines manually
python pipeline_monitor.py

# Open pipeline status in browser
python pipeline_monitor.py --open
```

**Automatische Überwachung**: Nach jedem `git push` werden Ihre CI/CD-Pipelines automatisch überwacht und Sie erhalten detailliertes Feedback über den Status.

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
