# MSIX Setup für Mauscribe
# Einfaches Setup-Skript für die erste MSIX-Installation

param(
    [switch]$SkipBuild = $false,
    [switch]$SkipInstall = $false
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Prüfe Voraussetzungen..." "Blue"
    
    # Prüfe Windows SDK
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
    if (-not (Test-Path $sdkPath)) {
        Write-ColorOutput "❌ Windows SDK nicht gefunden!" "Red"
        Write-ColorOutput "   Bitte installieren Sie das Windows 10 SDK von:" "Yellow"
        Write-ColorOutput "   https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" "Yellow"
        return $false
    }
    
    # Prüfe MakeAppx.exe
    $makeAppxPath = Join-Path $sdkPath "MakeAppx.exe"
    if (-not (Test-Path $makeAppxPath)) {
        Write-ColorOutput "❌ MakeAppx.exe nicht gefunden!" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ Alle Voraussetzungen erfüllt" "Green"
    return $true
}

function Build-MSIX {
    Write-ColorOutput "🔨 Erstelle MSIX-Paket..." "Blue"
    
    try {
        # Verwende Makefile für den Build
        make build-msix
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket erfolgreich erstellt" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Build fehlgeschlagen" "Red"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler beim MSIX-Build: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Install-MSIX {
    Write-ColorOutput "📥 Installiere MSIX-Paket..." "Blue"
    
    $msixPath = "dist\mauscribe.msix"
    
    if (-not (Test-Path $msixPath)) {
        Write-ColorOutput "❌ MSIX-Paket nicht gefunden: $msixPath" "Red"
        return $false
    }
    
    try {
        # Entferne alte Installation falls vorhanden
        $existingPackage = Get-AppxPackage -Name "Mauscribe.Robs" -ErrorAction SilentlyContinue
        if ($existingPackage) {
            Write-ColorOutput "🗑️ Entferne alte Installation..." "Yellow"
            Remove-AppxPackage -Package $existingPackage.PackageFullName
        }
        
        # Installiere neues Paket
        Add-AppxPackage -Path $msixPath
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket erfolgreich installiert" "Green"
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Installation fehlgeschlagen" "Red"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler bei Installation: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-Installation {
    Write-ColorOutput "🧪 Teste Installation..." "Blue"
    
    $package = Get-AppxPackage -Name "Mauscribe.Robs" -ErrorAction SilentlyContinue
    if ($package) {
        Write-ColorOutput "✅ Mauscribe MSIX-Paket gefunden:" "Green"
        Write-ColorOutput "   Name: $($package.Name)" "Cyan"
        Write-ColorOutput "   Version: $($package.Version)" "Cyan"
        Write-ColorOutput "   InstallLocation: $($package.InstallLocation)" "Cyan"
        return $true
    } else {
        Write-ColorOutput "❌ Mauscribe MSIX-Paket nicht gefunden" "Red"
        return $false
    }
}

function Show-NextSteps {
    Write-ColorOutput "`n🎉 MSIX-Installation abgeschlossen!" "Green"
    Write-ColorOutput "================================================" "Blue"
    Write-ColorOutput "Nächste Schritte:" "Blue"
    Write-ColorOutput "1. Starten Sie Mauscribe über das Start-Menü" "White"
    Write-ColorOutput "2. Oder verwenden Sie: mauscribe" "White"
    Write-ColorOutput "3. Konfigurieren Sie Ihre Maus-Buttons in config.toml" "White"
    Write-ColorOutput "4. Testen Sie die Audio-Aufnahme" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Für Updates verwenden Sie: make build-msix && make install-msix" "Cyan"
}

# Hauptfunktion
function Main {
    Write-ColorOutput "🚀 MSIX Setup für Mauscribe" "Blue"
    Write-ColorOutput "================================================" "Blue"
    
    # Prüfe Voraussetzungen
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Build MSIX-Paket
    if (-not $SkipBuild) {
        if (-not (Build-MSIX)) {
            exit 1
        }
    }
    
    # Installiere MSIX-Paket
    if (-not $SkipInstall) {
        if (-not (Install-MSIX)) {
            exit 1
        }
    }
    
    # Teste Installation
    if (Test-Installation) {
        Show-NextSteps
    } else {
        Write-ColorOutput "❌ Installation konnte nicht verifiziert werden" "Red"
        exit 1
    }
}

# Skript ausführen
Main
