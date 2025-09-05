# MSIX Assets Erstellung für Mauscribe
param(
    [string]$AssetsDir = "assets"
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Create-AssetFromIcon {
    param(
        [string]$SourceIcon,
        [string]$TargetAsset,
        [int]$Size = 150
    )
    
    if (Test-Path $SourceIcon) {
        try {
            # Verwende vorhandenes Icon als Basis
            Copy-Item $SourceIcon $TargetAsset -Force
            Write-ColorOutput "✅ Asset erstellt: $TargetAsset" "Green"
        } catch {
            Write-ColorOutput "⚠️ Fehler beim Erstellen von $TargetAsset" "Yellow"
        }
    } else {
        Write-ColorOutput "❌ Quell-Icon nicht gefunden: $SourceIcon" "Red"
    }
}

function Create-MSIXAssets {
    Write-ColorOutput "🎨 Erstelle MSIX-Assets..." "Blue"
    
    # Erstelle Assets-Verzeichnis falls nicht vorhanden
    if (-not (Test-Path $AssetsDir)) {
        New-Item -ItemType Directory -Path $AssetsDir -Force | Out-Null
    }
    
    # Basis-Icon-Pfad
    $baseIcon = "$AssetsDir\icons\mauscribe_icon.png"
    $baseIconIco = "$AssetsDir\icons\mauscribe_icon.ico"
    $baseIconSvg = "$AssetsDir\icons\mauscribe_icon.svg"
    
    # Erstelle fehlende Assets
    $requiredAssets = @(
        @{ Source = $baseIcon; Target = "$AssetsDir\StoreLogo.png" },
        @{ Source = $baseIcon; Target = "$AssetsDir\Square150x150Logo.png" },
        @{ Source = $baseIcon; Target = "$AssetsDir\Square44x44Logo.png" },
        @{ Source = $baseIcon; Target = "$AssetsDir\Wide310x150Logo.png" },
        @{ Source = $baseIcon; Target = "$AssetsDir\SplashScreen.png" }
    )
    
    foreach ($asset in $requiredAssets) {
        if (-not (Test-Path $asset.Target)) {
            Create-AssetFromIcon -SourceIcon $asset.Source -TargetAsset $asset.Target
        } else {
            Write-ColorOutput "ℹ️ Asset bereits vorhanden: $($asset.Target)" "Cyan"
        }
    }
    
    # Erstelle Cursor-Verzeichnis
    $cursorDir = "$AssetsDir\cursors"
    if (-not (Test-Path $cursorDir)) {
        New-Item -ItemType Directory -Path $cursorDir -Force | Out-Null
        Write-ColorOutput "📁 Cursor-Verzeichnis erstellt: $cursorDir" "Green"
    }
    
    Write-ColorOutput "✅ MSIX-Assets erstellt!" "Green"
}

# Hauptfunktion
Create-MSIXAssets
