<!-- cfc9234b-aa17-45e7-979b-35b0bc2a949a 3571ccc9-66ba-4c33-a6dd-95a9e8b313df -->
# Release Validation and Windows Installer Implementation

## Overview

Implement a comprehensive release validation system and create a professional Windows installer with configurable feature selection. Use WiX Toolset for MSI creation with Inno Setup as fallback.

## Phase 1: Release Validation System

### 1.1 Automated Validation Script

Create `tools/validate_release.py` (~300 lines):

- Check build artifacts exist and are valid
- Verify .exe file integrity (size, signature, dependencies)
- Run automated smoke tests on the built executable
- Validate all required files are included (settings.toml, icons, data/)
- Check version consistency across files (pyproject.toml, settings.toml, CHANGELOG.md)
- Generate validation report (JSON + Markdown)

### 1.2 Automated Integration Tests

Create `tests/integration/test_release.py` (~200 lines):

- Test executable launches without errors
- Test system tray initialization
- Test basic recording workflow (mock audio input)
- Test transcription service initialization
- Test settings persistence
- Test GUI opening and closing
- Test feature flags (audio database, enhanced mode)
- All tests run in isolated environment

### 1.3 Manual QA Checklist

Create `tools/qa_checklist.md`:

- Installation verification
- First-run experience
- Recording and transcription workflow
- System tray functionality
- GUI interactions (all tabs)
- Settings persistence
- Feature toggles
- Uninstallation cleanup
- Each item with pass/fail checkbox

### 1.4 Update Build Workflow

Modify `.github/workflows/build.yml`:

- Add validation step after build
- Run `validate_release.py` automatically
- Upload validation report as artifact
- Only proceed to release creation if validation passes
- Add manual approval gate for stable releases

## Phase 2: Windows Installer with WiX Toolset

### 2.1 WiX Configuration

Create `installer/mauscribe.wxs` (~400 lines):

- Product definition (name, version, manufacturer)
- Directory structure (Program Files, AppData, Start Menu)
- Component groups for features:
- Core (required): Mauscribe.exe, settings.toml, core icons
- Audio Database (optional): database files, enhanced audio features
- Enhanced Mode (optional): additional ML models, advanced features
- Whisper Models (optional): small, medium, large models (~1-3GB)
- Autostart (optional): registry keys for Windows startup
- Desktop Shortcuts (optional): desktop and start menu shortcuts
- Feature selection UI with descriptions
- Custom actions for first-run setup
- Uninstall cleanup (remove AppData, registry keys)

### 2.2 WiX Build Script

Create `installer/build_msi.py` (~150 lines):

- Download WiX Toolset if not present
- Compile .wxs to .wixobj using candle.exe
- Link .wixobj to .msi using light.exe
- Sign MSI if certificate available
- Validate MSI structure
- Generate installer metadata

### 2.3 Inno Setup Fallback

Create `installer/mauscribe.iss` (~300 lines):

- Same feature structure as WiX
- Custom wizard pages for feature selection
- Pascal script for conditional installation
- Registry entries for autostart
- Shortcuts creation
- Uninstall cleanup
- Simpler than WiX but less professional

### 2.4 Installer Build Workflow

Create `.github/workflows/installer.yml`:

- Trigger only on stable release tags (v*.*.* without -alpha/-beta)
- Build executable first
- Run validation tests
- Build MSI with WiX (try first)
- Build Inno Setup installer (fallback if WiX fails)
- Upload both installers as release assets
- Generate installation instructions

## Phase 3: Feature Management

### 3.1 Feature Manifest

Create `installer/features.json`:

- Define all installable features
- Dependencies between features
- File mappings for each feature
- Registry keys for each feature
- Size estimates for each feature
- Default selections

### 3.2 Post-Install Configuration

Create `tools/post_install.py` (~100 lines):

- Run after installation
- Configure settings.toml based on selected features
- Download Whisper models if selected
- Set up autostart if selected
- Create shortcuts if selected
- Show welcome screen with feature summary

## Phase 4: Integration and Testing

### 4.1 Update Release Manager

Modify `tools/release_manager.py`:

- Add installer build step
- Upload MSI and .exe to GitHub releases
- Generate installation instructions based on features
- Update release notes with installer info

### 4.2 End-to-End Test

Create `tests/e2e/test_installer.py` (~150 lines):

- Test MSI installation (silent mode)
- Verify all files installed correctly
- Test feature toggles work
- Test uninstallation
- Verify cleanup after uninstall
- Run in VM or container

### 4.3 Documentation

Update `README.md`:

- Installation instructions for MSI
- Feature selection guide
- System requirements
- Troubleshooting section

Create `docs/INSTALLER.md`:

- Detailed installer documentation
- Feature descriptions
- Advanced installation options
- Building installer from source

## Implementation Order

1. Create validation script and integration tests
2. Update build workflow with validation
3. Create WiX configuration and build script
4. Create Inno Setup fallback
5. Create installer build workflow
6. Implement feature management system
7. Update release manager for installer support
8. Create end-to-end tests
9. Update documentation
10. Test complete flow with test release

## Files to Create

- `tools/validate_release.py` - Release validation automation
- `tools/qa_checklist.md` - Manual QA checklist
- `tests/integration/test_release.py` - Integration tests
- `tests/e2e/test_installer.py` - End-to-end installer tests
- `installer/mauscribe.wxs` - WiX configuration
- `installer/build_msi.py` - MSI build automation
- `installer/mauscribe.iss` - Inno Setup fallback
- `installer/features.json` - Feature manifest
- `tools/post_install.py` - Post-installation setup
- `.github/workflows/installer.yml` - Installer build workflow
- `docs/INSTALLER.md` - Installer documentation

## Files to Modify

- `.github/workflows/build.yml` - Add validation step
- `tools/release_manager.py` - Add installer support
- `README.md` - Add installation instructions
- `pyproject.toml` - Add installer dependencies

## Success Criteria

- Validation catches common issues before release
- MSI installer works on Windows 10/11
- Feature selection properly configures installation
- Uninstaller removes all traces
- Automated tests pass consistently
- Manual QA checklist completed
- Documentation is clear and complete
- Release process takes ~2-3h including manual QA

## Key Technical Decisions

- WiX Toolset for professional MSI (industry standard)
- Inno Setup as reliable fallback (simpler, widely used)
- Feature-based installation (user choice)
- Automated validation before release (quality gate)
- Manual approval for stable releases (safety)
- Comprehensive testing at multiple levels (unit, integration, e2e)

### To-dos

- [ ] Create tools/validate_release.py with artifact validation and smoke tests
- [ ] Create tests/integration/test_release.py with automated release tests
- [ ] Create tools/qa_checklist.md with manual testing checklist
- [ ] Update .github/workflows/build.yml with validation step and manual approval
- [ ] Create installer/mauscribe.wxs with feature-based WiX configuration
- [ ] Create installer/build_msi.py to automate MSI compilation
- [ ] Create installer/mauscribe.iss as Inno Setup fallback
- [ ] Create .github/workflows/installer.yml for automated installer builds
- [ ] Create installer/features.json defining all installable features
- [ ] Create tools/post_install.py for post-installation configuration
- [ ] Modify tools/release_manager.py to support installer uploads
- [ ] Create tests/e2e/test_installer.py for end-to-end installer testing
- [ ] Update README.md and create docs/INSTALLER.md with installation guide
- [ ] Test complete release flow from validation to installer creation
