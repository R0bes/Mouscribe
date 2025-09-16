# PowerShell Script - Cursor Erscheinungsform ändern
# Autor: Mouscribe Assistant
# Beschreibung: Ändert den Windows-Cursor programmatisch

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Arrow", "Cross", "Hand", "IBeam", "Wait", "Help", "SizeAll", "SizeNESW", "SizeNS", "SizeNWSE", "SizeWE", "UpArrow", "No", "AppStarting", "Default", "Custom")]
    [string]$CursorType = "Default",
    
    [Parameter(Mandatory=$false)]
    [string]$CustomCursorPath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$RestoreDefault,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowAvailableCursors
)

# Windows API für Cursor-Manipulation
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class CursorAPI {
    [DllImport("user32.dll")]
    public static extern IntPtr LoadCursor(IntPtr hInstance, int lpCursorName);
    
    [DllImport("user32.dll")]
    public static extern IntPtr SetCursor(IntPtr hCursor);
    
    [DllImport("user32.dll")]
    public static extern IntPtr LoadCursorFromFile(string lpFileName);
    
    [DllImport("user32.dll")]
    public static extern bool SetSystemCursor(IntPtr hcur, uint id);
    
    [DllImport("user32.dll")]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);
    
    public const int IDC_ARROW = 32512;
    public const int IDC_IBEAM = 32513;
    public const int IDC_WAIT = 32514;
    public const int IDC_CROSS = 32515;
    public const int IDC_UPARROW = 32516;
    public const int IDC_SIZE = 32640;
    public const int IDC_ICON = 32641;
    public const int IDC_SIZENWSE = 32642;
    public const int IDC_SIZENESW = 32643;
    public const int IDC_SIZEWE = 32644;
    public const int IDC_SIZENS = 32645;
    public const int IDC_SIZEALL = 32646;
    public const int IDC_NO = 32648;
    public const int IDC_HAND = 32649;
    public const int IDC_APPSTARTING = 32650;
    public const int IDC_HELP = 32651;
    
    public const uint SPI_SETCURSORS = 0x0057;
    public const uint SPIF_UPDATEINIFILE = 0x01;
    public const uint SPIF_SENDCHANGE = 0x02;
}
"@

function Show-AvailableCursors {
    Write-Host "Verfügbare Cursor-Typen:" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    Write-Host "Arrow      - Standard-Pfeil" -ForegroundColor Yellow
    Write-Host "Cross      - Kreuz-Cursor" -ForegroundColor Yellow
    Write-Host "Hand       - Hand-Cursor" -ForegroundColor Yellow
    Write-Host "IBeam      - Text-Cursor (I-Strich)" -ForegroundColor Yellow
    Write-Host "Wait       - Warte-Cursor (Sanduhr)" -ForegroundColor Yellow
    Write-Host "Help       - Hilfe-Cursor (Pfeil mit Fragezeichen)" -ForegroundColor Yellow
    Write-Host "SizeAll    - Größe-ändern-Cursor (alle Richtungen)" -ForegroundColor Yellow
    Write-Host "SizeNESW   - Größe-ändern-Cursor (Nordost-Südwest)" -ForegroundColor Yellow
    Write-Host "SizeNS     - Größe-ändern-Cursor (Nord-Süd)" -ForegroundColor Yellow
    Write-Host "SizeNWSE   - Größe-ändern-Cursor (Nordwest-Südost)" -ForegroundColor Yellow
    Write-Host "SizeWE     - Größe-ändern-Cursor (West-Ost)" -ForegroundColor Yellow
    Write-Host "UpArrow    - Pfeil nach oben" -ForegroundColor Yellow
    Write-Host "No         - Verboten-Cursor" -ForegroundColor Yellow
    Write-Host "AppStarting- Anwendungsstart-Cursor" -ForegroundColor Yellow
    Write-Host "Default    - Standard-Cursor" -ForegroundColor Yellow
    Write-Host "Custom     - Benutzerdefinierter Cursor (benötigt Pfad)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Beispiele:" -ForegroundColor Cyan
    Write-Host ".\cursor_changer.ps1 -CursorType Hand" -ForegroundColor White
    Write-Host ".\cursor_changer.ps1 -CursorType Custom -CustomCursorPath 'C:\path\to\cursor.cur'" -ForegroundColor White
    Write-Host ".\cursor_changer.ps1 -RestoreDefault" -ForegroundColor White
}

function Set-SystemCursor {
    param(
        [string]$CursorType,
        [string]$CustomPath = ""
    )
    
    try {
        $cursorId = switch ($CursorType) {
            "Arrow" { [CursorAPI]::IDC_ARROW }
            "Cross" { [CursorAPI]::IDC_CROSS }
            "Hand" { [CursorAPI]::IDC_HAND }
            "IBeam" { [CursorAPI]::IDC_IBEAM }
            "Wait" { [CursorAPI]::IDC_WAIT }
            "Help" { [CursorAPI]::IDC_HELP }
            "SizeAll" { [CursorAPI]::IDC_SIZEALL }
            "SizeNESW" { [CursorAPI]::IDC_SIZENESW }
            "SizeNS" { [CursorAPI]::IDC_SIZENS }
            "SizeNWSE" { [CursorAPI]::IDC_SIZENWSE }
            "SizeWE" { [CursorAPI]::IDC_SIZEWE }
            "UpArrow" { [CursorAPI]::IDC_UPARROW }
            "No" { [CursorAPI]::IDC_NO }
            "AppStarting" { [CursorAPI]::IDC_APPSTARTING }
            "Default" { [CursorAPI]::IDC_ARROW }
            default { [CursorAPI]::IDC_ARROW }
        }
        
        if ($CursorType -eq "Custom" -and $CustomPath) {
            if (Test-Path $CustomPath) {
                $cursorHandle = [CursorAPI]::LoadCursorFromFile($CustomPath)
                if ($cursorHandle -ne [IntPtr]::Zero) {
                    [CursorAPI]::SetSystemCursor($cursorHandle, [CursorAPI]::IDC_ARROW)
                    Write-Host "✅ Benutzerdefinierter Cursor geladen: $CustomPath" -ForegroundColor Green
                } else {
                    Write-Host "❌ Fehler beim Laden des benutzerdefinierten Cursors" -ForegroundColor Red
                    return $false
                }
            } else {
                Write-Host "❌ Cursor-Datei nicht gefunden: $CustomPath" -ForegroundColor Red
                return $false
            }
        } else {
            # Standard-Cursor laden
            $cursorHandle = [CursorAPI]::LoadCursor([IntPtr]::Zero, $cursorId)
            if ($cursorHandle -ne [IntPtr]::Zero) {
                [CursorAPI]::SetSystemCursor($cursorHandle, [CursorAPI]::IDC_ARROW)
                Write-Host "✅ Cursor geändert zu: $CursorType" -ForegroundColor Green
            } else {
                Write-Host "❌ Fehler beim Laden des Cursors" -ForegroundColor Red
                return $false
            }
        }
        
        # System-Parameter aktualisieren
        [CursorAPI]::SystemParametersInfo([CursorAPI]::SPI_SETCURSORS, 0, [IntPtr]::Zero, [CursorAPI]::SPIF_UPDATEINIFILE -bor [CursorAPI]::SPIF_SENDCHANGE)
        
        return $true
    }
    catch {
        Write-Host "❌ Fehler beim Ändern des Cursors: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Restore-DefaultCursor {
    try {
        # Alle Standard-Cursor wiederherstellen
        $defaultCursors = @(
            @{Name="Arrow"; Id=[CursorAPI]::IDC_ARROW},
            @{Name="IBeam"; Id=[CursorAPI]::IDC_IBEAM},
            @{Name="Wait"; Id=[CursorAPI]::IDC_WAIT},
            @{Name="Cross"; Id=[CursorAPI]::IDC_CROSS},
            @{Name="UpArrow"; Id=[CursorAPI]::IDC_UPARROW},
            @{Name="Size"; Id=[CursorAPI]::IDC_SIZE},
            @{Name="SizeNWSE"; Id=[CursorAPI]::IDC_SIZENWSE},
            @{Name="SizeNESW"; Id=[CursorAPI]::IDC_SIZENESW},
            @{Name="SizeWE"; Id=[CursorAPI]::IDC_SIZEWE},
            @{Name="SizeNS"; Id=[CursorAPI]::IDC_SIZENS},
            @{Name="SizeAll"; Id=[CursorAPI]::IDC_SIZEALL},
            @{Name="No"; Id=[CursorAPI]::IDC_NO},
            @{Name="Hand"; Id=[CursorAPI]::IDC_HAND},
            @{Name="AppStarting"; Id=[CursorAPI]::IDC_APPSTARTING},
            @{Name="Help"; Id=[CursorAPI]::IDC_HELP}
        )
        
        foreach ($cursor in $defaultCursors) {
            $cursorHandle = [CursorAPI]::LoadCursor([IntPtr]::Zero, $cursor.Id)
            if ($cursorHandle -ne [IntPtr]::Zero) {
                [CursorAPI]::SetSystemCursor($cursorHandle, $cursor.Id)
            }
        }
        
        # System-Parameter aktualisieren
        [CursorAPI]::SystemParametersInfo([CursorAPI]::SPI_SETCURSORS, 0, [IntPtr]::Zero, [CursorAPI]::SPIF_UPDATEINIFILE -bor [CursorAPI]::SPIF_SENDCHANGE)
        
        Write-Host "✅ Standard-Cursor wiederhergestellt" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Fehler beim Wiederherstellen der Standard-Cursor: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Create-CustomCursor {
    param(
        [string]$OutputPath = "custom_cursor.cur"
    )
    
    try {
        # Einfacher benutzerdefinierter Cursor erstellen (16x16 Pixel)
        Add-Type -AssemblyName System.Drawing
        
        $bitmap = New-Object System.Drawing.Bitmap(32, 32)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        
        # Hintergrund transparent machen
        $graphics.Clear([System.Drawing.Color]::Transparent)
        
        # Einfaches Design zeichnen (Pfeil)
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 2)
        $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
        
        # Pfeil zeichnen
        $points = @(
            [System.Drawing.Point]::new(2, 2),
            [System.Drawing.Point]::new(2, 28),
            [System.Drawing.Point]::new(8, 22),
            [System.Drawing.Point]::new(16, 30),
            [System.Drawing.Point]::new(24, 22),
            [System.Drawing.Point]::new(30, 28),
            [System.Drawing.Point]::new(30, 2),
            [System.Drawing.Point]::new(2, 2)
        )
        
        $graphics.FillPolygon($brush, $points)
        
        # Speichern als ICO-Datei (vereinfacht)
        $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        
        $graphics.Dispose()
        $bitmap.Dispose()
        
        Write-Host "✅ Benutzerdefinierter Cursor erstellt: $OutputPath" -ForegroundColor Green
        return $OutputPath
    }
    catch {
        Write-Host "❌ Fehler beim Erstellen des benutzerdefinierten Cursors: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Hauptlogik
Write-Host "🖱️  Mouscribe Cursor Changer" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

if ($ShowAvailableCursors) {
    Show-AvailableCursors
    exit 0
}

if ($RestoreDefault) {
    Write-Host "Wiederherstelle Standard-Cursor..." -ForegroundColor Yellow
    if (Restore-DefaultCursor) {
        Write-Host "✅ Erfolgreich!" -ForegroundColor Green
    } else {
        Write-Host "❌ Fehler beim Wiederherstellen!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Ändere Cursor zu: $CursorType" -ForegroundColor Yellow
    
    if ($CursorType -eq "Custom") {
        if (-not $CustomCursorPath) {
            Write-Host "Erstelle benutzerdefinierten Cursor..." -ForegroundColor Yellow
            $CustomCursorPath = Create-CustomCursor
            if (-not $CustomCursorPath) {
                Write-Host "❌ Konnte keinen benutzerdefinierten Cursor erstellen!" -ForegroundColor Red
                exit 1
            }
        }
    }
    
    if (Set-SystemCursor -CursorType $CursorType -CustomPath $CustomCursorPath) {
        Write-Host "✅ Cursor erfolgreich geändert!" -ForegroundColor Green
    } else {
        Write-Host "❌ Fehler beim Ändern des Cursors!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "💡 Tipp: Verwende -RestoreDefault um die Standard-Cursor wiederherzustellen" -ForegroundColor Cyan
Write-Host "💡 Tipp: Verwende -ShowAvailableCursors um alle verfügbaren Optionen zu sehen" -ForegroundColor Cyan
