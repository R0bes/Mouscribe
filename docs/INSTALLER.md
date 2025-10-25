# Mauscribe Installer Documentation

## Overview

Mauscribe provides professional Windows installers with configurable feature selection. The installer system supports both MSI (WiX Toolset) and Inno Setup formats, allowing users to choose which features to install.

## Installer Types

### MSI Installer (Recommended)
- **File**: `Mauscribe-{version}.msi`
- **Type**: Windows Installer Package
- **Features**: Professional installation with feature selection
- **Requirements**: Windows 7 or later
- **Advantages**:
  - Industry standard Windows installer
  - Proper Windows integration
  - Feature-based installation
  - Automatic dependency management
  - Clean uninstallation

### Inno Setup Installer (Alternative)
- **File**: `Mauscribe-{version}-Setup.exe`
- **Type**: Executable Installer
- **Features**: Simple installation wizard
- **Requirements**: Windows 7 or later
- **Advantages**:
  - Smaller file size
  - Faster installation
  - Simple wizard interface
  - No additional dependencies

## Installation Features

### Core Application (Required)
Essential Mauscribe functionality including:
- Voice recording and transcription
- System tray integration
- Basic UI components
- Core settings and configuration

**Size**: ~50MB

### Audio Database (Optional)
Store and manage recorded audio files:
- Audio file storage and playback
- Retranscription capabilities
- File management interface
- Database integration

**Size**: ~10MB
**Dependencies**: Core Application

### Enhanced Mode (Optional)
Advanced transcription features:
- Better transcription quality
- Noise reduction
- Extended language support
- Advanced audio processing

**Size**: ~20MB
**Dependencies**: Core Application

### Whisper Models (Optional)
AI-powered transcription models:
- Small model (~500MB)
- Medium model (~1.5GB)
- Large model (~3GB)
- Improved transcription accuracy

**Size**: ~1.5GB total
**Dependencies**: Core Application
**Note**: Models are downloaded during installation

### Desktop Shortcuts (Optional)
Create desktop and start menu shortcuts:
- Desktop shortcut
- Start menu entry
- Quick launch integration

**Size**: Minimal
**Dependencies**: Core Application

### Start with Windows (Optional)
Automatically start Mauscribe when Windows boots:
- Registry integration
- Silent startup
- Background operation

**Size**: Minimal
**Dependencies**: Core Application

### UI Icons (Optional)
Additional UI icons for interface elements:
- Button icons
- Status indicators
- Interface enhancements

**Size**: ~5MB
**Dependencies**: Core Application

## System Requirements

### Minimum Requirements
- **OS**: Windows 7 SP1 or later
- **Architecture**: x64 or x86
- **RAM**: 2GB
- **Disk Space**: 2GB free
- **Audio**: Microphone access
- **Network**: Internet connection (for model downloads)

### Recommended Requirements
- **OS**: Windows 10 or later
- **Architecture**: x64
- **RAM**: 4GB or more
- **Disk Space**: 5GB free
- **Audio**: High-quality microphone
- **Network**: Stable internet connection

## Installation Process

### MSI Installation

1. **Download** the MSI installer from the release page
2. **Run** the installer as Administrator
3. **Select Features**:
   - Choose which features to install
   - Review size estimates
   - Configure installation directory
4. **Install**:
   - Wait for installation to complete
   - Review installation summary
5. **Configure**:
   - Run post-installation setup
   - Download Whisper models (if selected)
   - Configure autostart (if selected)

### Inno Setup Installation

1. **Download** the Setup executable from the release page
2. **Run** the installer
3. **Follow Wizard**:
   - Accept license agreement
   - Choose installation directory
   - Select features
   - Configure shortcuts
4. **Install**:
   - Wait for installation to complete
5. **Finish**:
   - Launch application (optional)
   - View readme (optional)

## Silent Installation

### MSI Silent Installation
```cmd
msiexec /i Mauscribe-1.0.0.msi /quiet /norestart INSTALLDIR="C:\Program Files\Mauscribe"
```

### MSI with Feature Selection
```cmd
msiexec /i Mauscribe-1.0.0.msi /quiet /norestart ADDLOCAL=CoreFeature,AudioDatabaseFeature,UIIconsFeature
```

### Inno Setup Silent Installation
```cmd
Mauscribe-1.0.0-Setup.exe /SILENT /DIR="C:\Program Files\Mauscribe"
```

## Feature Configuration

### Registry Settings
The installer creates registry entries under `HKEY_CURRENT_USER\Software\Mauscribe`:

- **Version**: Installed version
- **InstallPath**: Installation directory
- **Settings**: Feature-specific settings

### Settings File
The installer updates `settings.toml` based on selected features:

```toml
[ui]
enable_audio_files_tab = true    # If Audio Database installed
enable_audio_database = true     # If Audio Database installed
enable_enhanced_mode = true      # If Enhanced Mode installed
auto_start_gui = true           # If Autostart installed
```

## Uninstallation

### MSI Uninstallation
1. **Control Panel**: Programs and Features
2. **Select** Mauscribe
3. **Click** Uninstall
4. **Confirm** uninstallation

### Inno Setup Uninstallation
1. **Start Menu**: Mauscribe → Uninstall
2. **Confirm** uninstallation

### Silent Uninstallation
```cmd
# MSI
msiexec /x {ProductCode} /quiet

# Inno Setup
unins000.exe /SILENT
```

## Troubleshooting

### Common Issues

#### Installation Fails
- **Run as Administrator**: Right-click installer → "Run as administrator"
- **Disable Antivirus**: Temporarily disable real-time protection
- **Check Disk Space**: Ensure sufficient free space
- **Windows Updates**: Install latest Windows updates

#### Features Not Working
- **Reinstall**: Uninstall and reinstall with feature selection
- **Registry**: Check registry entries in `HKEY_CURRENT_USER\Software\Mauscribe`
- **Settings**: Verify `settings.toml` configuration

#### Whisper Models Not Downloading
- **Internet Connection**: Ensure stable internet connection
- **Firewall**: Check firewall settings
- **Proxy**: Configure proxy settings if needed
- **Manual Download**: Download models manually from Hugging Face

#### Autostart Not Working
- **Registry**: Check `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- **Task Manager**: Verify startup entry
- **Reinstall**: Reinstall with autostart feature

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 1603 | Fatal error during installation | Run as Administrator, check disk space |
| 1618 | Another installation in progress | Wait for other installation to complete |
| 1619 | Installation package could not be opened | Re-download installer, check file integrity |
| 1622 | Error opening installation log file | Check file permissions, disk space |

### Log Files
- **MSI Log**: `%TEMP%\MSI*.log`
- **Inno Setup Log**: `%TEMP%\Setup Log *.txt`
- **Application Log**: `%LOCALAPPDATA%\Mauscribe\logs\`

## Advanced Configuration

### Custom Installation Directory
```cmd
# MSI
msiexec /i Mauscribe-1.0.0.msi INSTALLDIR="D:\Custom\Mauscribe"

# Inno Setup
Mauscribe-1.0.0-Setup.exe /DIR="D:\Custom\Mauscribe"
```

### Feature Selection
```cmd
# MSI - Install specific features
msiexec /i Mauscribe-1.0.0.msi ADDLOCAL=CoreFeature,AudioDatabaseFeature

# MSI - Exclude features
msiexec /i Mauscribe-1.0.0.msi ADDLOCAL=ALL REMOVE=WhisperModelsFeature
```

### Post-Installation Configuration
The installer runs `tools/post_install.py` to:
- Update settings based on installed features
- Download Whisper models (if selected)
- Create AppData directory structure
- Configure autostart (if selected)

## Building Installers

### Prerequisites
- **WiX Toolset**: For MSI creation
- **Inno Setup**: For executable installer
- **Python**: For build scripts
- **Windows**: Build environment

### Build Process
```bash
# Build MSI
python installer/build_msi.py --version 1.0.0 --output-dir dist

# Build Inno Setup
iscc installer/mauscribe.iss
```

### Automated Build
The installer build process is automated via GitHub Actions:
- Triggered on successful release builds
- Creates both MSI and Inno Setup installers
- Uploads installers to GitHub releases
- Generates installation instructions

## Support

### Getting Help
- **GitHub Issues**: [Report problems](https://github.com/R0bes/Mauscribe/issues)
- **Documentation**: Check this guide and README.md
- **Logs**: Check application and installer logs

### Contributing
- **Bug Reports**: Include installer logs and system information
- **Feature Requests**: Describe desired installer features
- **Pull Requests**: Follow contribution guidelines

## License

The installer and installation process are covered by the same MIT license as Mauscribe itself.
