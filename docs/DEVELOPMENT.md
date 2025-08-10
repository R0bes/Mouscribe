# Development Documentation

## Project Overview

Mauscribe is a voice-to-text tool designed for efficient text input and multi-agent AI workflows.

## Architecture

### Core Components

- **Main Application** (`src/main.py`): Central application logic and system tray integration
- **Sound Controller** (`src/sound_controller.py`): System volume management
- **Input Handler** (`src/input_handler.py`): Mouse and keyboard event processing
- **Speech-to-Text** (`src/stt.py`): Audio transcription using Whisper
- **Recorder** (`src/recorder.py`): Audio recording functionality
- **Configuration** (`src/config.py`): Settings management
- **Spell Checker** (`src/spell_checker.py`): Text correction and validation
- **Updater** (`src/updater.py`): Automatic update functionality

### Data Flow

1. User triggers recording (mouse button/keyboard)
2. Audio is captured and processed
3. Speech is transcribed to text
4. Text is spell-checked and corrected
5. Result is copied to clipboard
6. User pastes text with double-click

## Development Setup

### Prerequisites

- Python 3.8+
- Windows OS (primary target)
- Git

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd mauscribe

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Code Style

- **Comments**: English, concise, meaningful
- **Formatting**: Follow PEP 8 guidelines
- **Documentation**: Docstrings for all public functions
- **Type Hints**: Use type annotations where beneficial

## Testing

### Manual Testing

```bash
# Start application
python main.py

# Test recording functionality
# Test volume management
# Test system tray integration
```

### Automated Testing

```bash
# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=src
```

## Building

### Executable Creation

```bash
# Build .exe file
python build.py

# Output: dist/mauscribe.exe
```

### Build Process

1. Check PyInstaller availability
2. Clean previous builds
3. Compile with icon embedding
4. Test executable functionality

## Configuration

### TOML Structure

```toml
[input]
method = "mouse_button"

[mouse_button]
primary = "x2"
secondary = "x1"

[audio]
sample_rate = 16000
channels = 1

[stt]
model_size = "base"
compute_type = "int8"
```

### Environment Variables

- `MAUSCRIBE_CONFIG_PATH`: Custom config file location
- `MAUSCRIBE_LOG_LEVEL`: Logging verbosity

## Deployment

### Release Process

1. Update version in configuration
2. Run tests
3. Build executable
4. Create release tag
5. Upload assets

### Distribution

- **Windows**: .exe installer
- **Source**: Python package
- **Documentation**: GitHub Pages

## Troubleshooting

### Common Issues

- **Volume not restored**: Check audio device permissions
- **Cursor not changing**: Verify Windows compatibility
- **Build failures**: Ensure PyInstaller is installed

### Debug Mode

Enable debug logging in `config.toml`:

```toml
[debug]
enabled = true
level = "DEBUG"
```

## Contributing

### Development Workflow

1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Review

- All changes require review
- Tests must pass
- Documentation updated
- No breaking changes

## Performance

### Optimization Areas

- Audio processing pipeline
- Memory management
- UI responsiveness
- Startup time

### Monitoring

- CPU usage during recording
- Memory consumption
- Audio latency
- Transcription accuracy

## Security

### Considerations

- Audio data handling
- System permissions
- Update verification
- User privacy

### Best Practices

- Minimal permission requests
- Secure update channels
- No data collection
- Local processing only
