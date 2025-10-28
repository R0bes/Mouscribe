; Inno Setup Script for Mauscribe
; Fallback installer when WiX Toolset is not available

#define MyAppName "Mauscribe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Robs"
#define MyAppURL "https://github.com/R0bes/Mauscribe"
#define MyAppExeName "Mauscribe.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{12345678-1234-1234-1234-123456789012}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=Mauscribe-{#MyAppVersion}-Setup
SetupIconFile=dist\src\ui\icons\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
MinVersion=6.1sp1
ArchitecturesAllowed=x64 x86
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "autostart"; Description: "Start Mauscribe with Windows"; GroupDescription: "Startup Options"; Flags: unchecked

; Audio Database feature
Name: "audio_database"; Description: "Install Audio Database feature"; GroupDescription: "Features"; Flags: checked

; Whisper Model downloads (optional)
Name: "whisper_tiny"; Description: "Tiny (39 MB) - Schnellste"; GroupDescription: "Whisper-Modelle (optional)"; Flags: unchecked
Name: "whisper_base"; Description: "Base (74 MB) - Ausgewogen"; GroupDescription: "Whisper-Modelle (optional)"; Flags: unchecked
Name: "whisper_small"; Description: "Small (244 MB) - Gut"; GroupDescription: "Whisper-Modelle (optional)"; Flags: unchecked
Name: "whisper_medium"; Description: "Medium (769 MB) - Sehr gut"; GroupDescription: "Whisper-Modelle (optional)"; Flags: checked
Name: "whisper_large"; Description: "Large (1550 MB) - Beste Qualität"; GroupDescription: "Whisper-Modelle (optional)"; Flags: unchecked

; Other features
Name: "enhanced_mode"; Description: "Install Enhanced Mode feature"; GroupDescription: "Features"; Flags: unchecked
Name: "ui_icons"; Description: "Install additional UI icons"; GroupDescription: "Features"; Flags: checked

[Files]
; Core application files (always installed)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\settings.toml"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_idle.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_record.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_16.png"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_32.png"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_64.png"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_128.png"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "dist\src\ui\icons\icon_256.png"; DestDir: "{app}\icons"; Flags: ignoreversion

; Audio Database feature (conditional)
Source: "dist\data\audio_database.db"; DestDir: "{app}\data"; Flags: ignoreversion; Tasks: audio_database
Source: "dist\data\audio\*"; DestDir: "{app}\data\audio"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: audio_database

; UI Icons feature (conditional)
Source: "dist\src\ui\icons\ui\play_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\play_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\play_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\pause_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\pause_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\pause_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\stop_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\stop_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\stop_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\edit_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\edit_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\edit_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\copy_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\copy_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\copy_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\refresh_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\refresh_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\refresh_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\delete_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\delete_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\delete_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\settings_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\settings_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\settings_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_success_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_success_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_success_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_error_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_error_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_error_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_warning_16.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_warning_24.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons
Source: "dist\src\ui\icons\ui\status_warning_32.png"; DestDir: "{app}\ui_icons"; Flags: ignoreversion; Tasks: ui_icons

; Post-install script
Source: "tools\post_install.py"; DestDir: "{app}\tools"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\icon.ico"; Tasks: quicklaunchicon

[Registry]
; Autostart registry entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Mauscribe"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletevalue; Tasks: autostart

; Application settings
Root: HKCU; Subkey: "Software\Mauscribe"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\Mauscribe"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

; Feature selections
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "audio_database"; ValueData: 1; Tasks: audio_database
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "enhanced_mode"; ValueData: 1; Tasks: enhanced_mode
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "ui_icons"; ValueData: 1; Tasks: ui_icons

; Whisper model selections
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "whisper_tiny"; ValueData: 1; Tasks: whisper_tiny
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "whisper_base"; ValueData: 1; Tasks: whisper_base
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "whisper_small"; ValueData: 1; Tasks: whisper_small
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "whisper_medium"; ValueData: 1; Tasks: whisper_medium
Root: HKCU; Subkey: "Software\Mauscribe\Settings"; ValueType: dword; ValueName: "whisper_large"; ValueData: 1; Tasks: whisper_large

[Run]
; Post-install actions
Filename: "python"; Parameters: """{app}\tools\post_install.py"""; WorkingDir: "{app}"; Flags: runhidden; Description: "Configure Mauscribe settings"

; Optional: Start application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up application data
Type: filesandordirs; Name: "{localappdata}\Mauscribe"
Type: filesandordirs; Name: "{app}\data\audio"
Type: filesandordirs; Name: "{app}\models"

[Code]
// Custom functions for Inno Setup

function InitializeSetup(): Boolean;
begin
  Result := True;

  // Check if Mauscribe is already running
  if CheckForMutexes('MauscribeMutex') then
  begin
    if MsgBox('Mauscribe is currently running. Please close it before continuing with the installation.', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;

  // Check if Mauscribe is running during uninstall
  if CheckForMutexes('MauscribeMutex') then
  begin
    if MsgBox('Mauscribe is currently running. Please close it before continuing with the uninstallation.', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Additional post-install actions can be added here
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;

  // Skip the Ready to Install page if running silently
  if (PageID = wpReady) and WizardSilent then
    Result := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  // Custom page handling
  if CurPageID = wpSelectTasks then
  begin
    // Update task descriptions based on selections
  end;
end;

function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usPostUninstall:
      begin
        // Additional cleanup after uninstall
        DelTree(ExpandConstant('{localappdata}\Mauscribe'), True, True, True);
      end;
  end;
end;
