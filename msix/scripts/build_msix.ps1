# MSIX Build-Skript für Mauscribe
param(
    [string]$Version = "1.0.0.0",
    [string]$Configuration = "Release",
    [string]$Publisher = "CN=Robs",
    [switch]$Sign = $true,
    [switch]$Test = $false
)

# Farben für bessere Lesbarkeit
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Konstanten
$BytesPerMB = 1024 * 1024  # 1 MB = 1024 KB = 1024 * 1024 Bytes

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Prüfe Voraussetzungen..." $Blue
    
    # Prüfe Windows SDK
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
    if (-not (Test-Path $sdkPath)) {
        Write-ColorOutput "❌ Windows SDK nicht gefunden!" $Red
        Write-ColorOutput "   Bitte installieren Sie das Windows 10 SDK" $Yellow
        return $false
    }
    
    # Prüfe MakeAppx.exe
    $makeAppxPath = Join-Path $sdkPath "MakeAppx.exe"
    if (-not (Test-Path $makeAppxPath)) {
        Write-ColorOutput "❌ MakeAppx.exe nicht gefunden!" $Red
        return $false
    }
    
    # Prüfe SignTool.exe
    $signToolPath = Join-Path $sdkPath "SignTool.exe"
    if (-not (Test-Path $signToolPath)) {
        Write-ColorOutput "❌ SignTool.exe nicht gefunden!" $Red
        return $false
    }
    
    Write-ColorOutput "✅ Alle Voraussetzungen erfüllt" $Green
    return $true
}

function Build-PyInstaller {
    Write-ColorOutput "🔨 Erstelle PyInstaller Build..." $Blue
    
    # Aktuelle Umgebung
    $env:PYTHONPATH = "src"
    $env:MAUSCRIBE_VERSION = $Version
    
    # PyInstaller Build
    try {
        pyinstaller mauscribe.spec --clean --distpath "dist\msix_temp"
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ PyInstaller Build erfolgreich" $Green
            return $true
        } else {
            Write-ColorOutput "❌ PyInstaller Build fehlgeschlagen" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler beim PyInstaller Build: $($_.Exception.Message)" $Red
        return $false
    }
}

function Prepare-MSIXAssets {
    Write-ColorOutput "📁 Bereite MSIX-Assets vor..." $Blue
    
    $msixDir = "dist\msix_temp"
    $assetsDir = "assets"
    
    # Erstelle Assets automatisch falls nicht vorhanden
    if (-not (Test-Path "$assetsDir\StoreLogo.png")) {
        Write-ColorOutput "🎨 Erstelle fehlende Assets..." $Yellow
        & "msix\scripts\create_assets.ps1"
    }
    
    # Erstelle Assets-Verzeichnis im MSIX-Build
    $msixAssetsDir = Join-Path $msixDir "assets"
    New-Item -ItemType Directory -Path $msixAssetsDir -Force | Out-Null
    
    # Kopiere Icons
    $iconsDir = Join-Path $msixAssetsDir "icons"
    New-Item -ItemType Directory -Path $iconsDir -Force | Out-Null
    if (Test-Path "$assetsDir\icons") {
        Copy-Item "$assetsDir\icons\*" $iconsDir -Recurse -Force
    }
    
    # Kopiere alle Assets
    if (Test-Path $assetsDir) {
        Copy-Item "$assetsDir\*" $msixAssetsDir -Recurse -Force -Exclude "icons"
    }
    
    Write-ColorOutput "✅ MSIX-Assets vorbereitet" $Green
}

function Update-Manifest {
    Write-ColorOutput "📝 Aktualisiere Manifest..." $Blue
    
    $manifestPath = "msix\manifest\AppxManifest.xml"
    $tempManifestPath = "dist\msix_temp\AppxManifest.xml"
    
    # Kopiere Manifest
    Copy-Item $manifestPath $tempManifestPath -Force
    
    # Aktualisiere Version im Manifest
    $manifestContent = Get-Content $tempManifestPath -Raw
    $manifestContent = $manifestContent -replace 'Version="[^"]*"', "Version=`"$Version`""
    $manifestContent = $manifestContent -replace 'Publisher="[^"]*"', "Publisher=`"$Publisher`""
    Set-Content $tempManifestPath $manifestContent -Encoding UTF8
    
    Write-ColorOutput "✅ Manifest aktualisiert" $Green
}

function Create-MSIXPackage {
    Write-ColorOutput "📦 Erstelle MSIX-Paket..." $Blue
    
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
    $makeAppxPath = Join-Path $sdkPath "MakeAppx.exe"
    $msixDir = "dist\msix_temp"
    $outputPath = "dist\mauscribe.msix"
    
    try {
        & $makeAppxPath pack /d $msixDir /p $outputPath /l
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket erstellt: $outputPath" $Green
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Paket-Erstellung fehlgeschlagen" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler beim MSIX-Paket: $($_.Exception.Message)" $Red
        return $false
    }
}

function Sign-MSIXPackage {
    param([string]$CertificatePath, [string]$MsixPath)
    
    Write-ColorOutput "🔐 Signiere MSIX-Paket..." $Blue
    
    $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
    $signToolPath = Join-Path $sdkPath "SignTool.exe"
    
    # Erstelle Zertifikat falls nicht vorhanden
    if (-not (Test-Path $CertificatePath)) {
        Write-ColorOutput "🔑 Erstelle Self-Signed Zertifikat..." $Yellow
        try {
            $cert = New-SelfSignedCertificate -Subject "CN=Mauscribe" -CertStoreLocation "Cert:\LocalMachine\My" -Type CodeSigningCert
            Export-PfxCertificate -Cert $cert -FilePath $CertificatePath -Password (ConvertTo-SecureString -String "mauscribe123" -AsPlainText -Force)
            Write-ColorOutput "✅ Zertifikat erstellt" $Green
        } catch {
            Write-ColorOutput "❌ Fehler beim Zertifikat: $($_.Exception.Message)" $Red
            return $false
        }
    }
    
    # Signiere MSIX-Paket
    try {
        & $signToolPath sign /f $CertificatePath /p "mauscribe123" $MsixPath
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket signiert" $Green
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Signierung fehlgeschlagen" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler beim Signieren: $($_.Exception.Message)" $Red
        return $false
    }
}

function Test-MSIXPackage {
    Write-ColorOutput "🧪 Teste MSIX-Paket..." $Blue
    
    $msixPath = "dist\mauscribe.msix"
    
    # Prüfe Paket-Größe
    $fileSizeBytes = (Get-Item $msixPath).Length
    $fileSizeMB = [math]::Round($fileSizeBytes / $BytesPerMB, 2)
    Write-ColorOutput "📊 Paket-Größe: $fileSizeMB MB" $Blue
    
    if ($fileSizeMB -gt 500) {
        Write-ColorOutput "⚠️  Paket ist sehr groß (>500MB)" $Yellow
    }
    
    # Validiere Paket
    try {
        $sdkPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64"
        $makeAppxPath = Join-Path $sdkPath "MakeAppx.exe"
        & $makeAppxPath unpack /p $msixPath /d "dist\msix_test" /l
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket ist gültig" $Green
            Remove-Item "dist\msix_test" -Recurse -Force
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Paket ist ungültig" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler beim Testen: $($_.Exception.Message)" $Red
        return $false
    }
}

function Install-MSIXPackage {
    Write-ColorOutput "📥 Installiere MSIX-Paket..." $Blue
    
    $msixPath = "dist\mauscribe.msix"
    
    try {
        # Entferne alte Installation falls vorhanden
        $existingPackage = Get-AppxPackage -Name "Mauscribe.Robs" -ErrorAction SilentlyContinue
        if ($existingPackage) {
            Write-ColorOutput "🗑️  Entferne alte Installation..." $Yellow
            Remove-AppxPackage -Package $existingPackage.PackageFullName
        }
        
        # Installiere neues Paket
        Add-AppxPackage -Path $msixPath
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MSIX-Paket installiert" $Green
            return $true
        } else {
            Write-ColorOutput "❌ MSIX-Installation fehlgeschlagen" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Fehler bei Installation: $($_.Exception.Message)" $Red
        return $false
    }
}

# Hauptfunktion
function Main {
    Write-ColorOutput "🚀 Starte MSIX Build für Mauscribe v$Version" $Blue
    Write-ColorOutput "================================================" $Blue
    
    # Prüfe Voraussetzungen
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Erstelle Build-Verzeichnis
    $buildDir = "dist\msix_temp"
    if (Test-Path $buildDir) {
        Remove-Item $buildDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
    
    # Build-Schritte
    $steps = @(
        @{ Name = "PyInstaller Build"; Function = "Build-PyInstaller" },
        @{ Name = "MSIX Assets"; Function = "Prepare-MSIXAssets" },
        @{ Name = "Manifest Update"; Function = "Update-Manifest" },
        @{ Name = "MSIX Package"; Function = "Create-MSIXPackage" }
    )
    
    foreach ($step in $steps) {
        Write-ColorOutput "`n📋 $($step.Name)..." $Blue
        if (-not (& $step.Function)) {
            Write-ColorOutput "❌ Build fehlgeschlagen bei: $($step.Name)" $Red
            exit 1
        }
    }
    
    # Signierung
    if ($Sign) {
        Write-ColorOutput "`n📋 Signierung..." $Blue
        $certPath = "msix\certificates\mauscribe.pfx"
        $msixPath = "dist\mauscribe.msix"
        if (-not (Sign-MSIXPackage -CertificatePath $certPath -MsixPath $msixPath)) {
            Write-ColorOutput "❌ Signierung fehlgeschlagen" $Red
            exit 1
        }
    }
    
    # Test
    if ($Test) {
        Write-ColorOutput "`n📋 Testing..." $Blue
        if (-not (Test-MSIXPackage)) {
            Write-ColorOutput "❌ Testing fehlgeschlagen" $Red
            exit 1
        }
        
        # Installation testen
        if (-not (Install-MSIXPackage)) {
            Write-ColorOutput "❌ Installation fehlgeschlagen" $Red
            exit 1
        }
    }
    
    # Aufräumen
    if (Test-Path $buildDir) {
        Remove-Item $buildDir -Recurse -Force
    }
    
    Write-ColorOutput "`n🎉 MSIX Build erfolgreich abgeschlossen!" $Green
    Write-ColorOutput "📦 Paket: dist\mauscribe.msix" $Blue
    $finalSizeBytes = (Get-Item 'dist\mauscribe.msix').Length
    $finalSizeMB = [math]::Round($finalSizeBytes / $BytesPerMB, 2)
    Write-ColorOutput "📊 Größe: $finalSizeMB MB" $Blue
}

# Skript ausführen
Main
