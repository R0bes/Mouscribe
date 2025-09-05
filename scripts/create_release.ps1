# MSIX Release Script für Mauscribe
# Erstellt automatisch Git-Tags und GitHub Releases

param(
    [switch]$Force = $false
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-ColorOutput "Prüfe Voraussetzungen..." "Blue"
    
    # Prüfe Git
    try {
        $gitVersion = git --version
        Write-ColorOutput "Git gefunden: $gitVersion" "Green"
    } catch {
        Write-ColorOutput "Git nicht gefunden!" "Red"
        return $false
    }
    
    # Prüfe Python
    try {
        $pythonVersion = python --version
        Write-ColorOutput "Python gefunden: $pythonVersion" "Green"
    } catch {
        Write-ColorOutput "Python nicht gefunden!" "Red"
        return $false
    }
    
    # Prüfe pyproject.toml
    if (-not (Test-Path "pyproject.toml")) {
        Write-ColorOutput "pyproject.toml nicht gefunden!" "Red"
        return $false
    }
    
    # Prüfe Git-Status
    $gitStatus = git status --porcelain
    if ($gitStatus -and -not $Force) {
        Write-ColorOutput "Uncommitted changes gefunden:" "Yellow"
        Write-ColorOutput $gitStatus "Yellow"
        Write-ColorOutput "Verwenden Sie -Force um trotzdem fortzufahren" "Yellow"
        return $false
    }
    
    # Prüfe Branch
    $currentBranch = git branch --show-current
    if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
        Write-ColorOutput "Nicht auf main/master branch: $currentBranch" "Yellow"
        if (-not $Force) {
            Write-ColorOutput "Verwenden Sie -Force um trotzdem fortzufahren" "Yellow"
            return $false
        }
    }
    
    Write-ColorOutput "Alle Voraussetzungen erfüllt" "Green"
    return $true
}

function Get-Version {
    Write-ColorOutput "Lese Version aus pyproject.toml..." "Blue"
    
    try {
        $version = python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"
        Write-ColorOutput "Version gefunden: $version" "Green"
        return $version
    } catch {
        Write-ColorOutput "Fehler beim Lesen der Version: $($_.Exception.Message)" "Red"
        return $null
    }
}

function Create-GitTag {
    param([string]$Version)
    
    Write-ColorOutput "Erstelle Git-Tag: v$Version" "Blue"
    
    try {
        # Prüfe ob Tag bereits existiert
        $existingTag = git tag -l "v$Version"
        if ($existingTag) {
            Write-ColorOutput "Tag v$Version existiert bereits" "Yellow"
            if (-not $Force) {
                Write-ColorOutput "Verwenden Sie -Force um Tag zu überschreiben" "Yellow"
                return $false
            }
            git tag -d "v$Version"
            Write-ColorOutput "Alten Tag gelöscht" "Yellow"
        }
        
        # Erstelle neuen Tag
        git tag "v$Version"
        Write-ColorOutput "Git-Tag erstellt: v$Version" "Green"
        return $true
    } catch {
        Write-ColorOutput "Fehler beim Erstellen des Tags: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Push-GitTag {
    param([string]$Version)
    
    Write-ColorOutput "Pushe Tag zu GitHub..." "Blue"
    
    try {
        git push origin "v$Version"
        Write-ColorOutput "Tag gepusht: v$Version" "Green"
        return $true
    } catch {
        Write-ColorOutput "Fehler beim Pushen des Tags: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Get-GitHubRepo {
    try {
        $remoteUrl = git config --get remote.origin.url
        if ($remoteUrl -match 'github\.com[:/]([^/]*)/([^/]*?)\.git') {
            return "$matches[1]/$matches[2]"
        } elseif ($remoteUrl -match 'github\.com[:/]([^/]*)/([^/]*?)') {
            return "$matches[1]/$matches[2]"
        }
        return $null
    } catch {
        return $null
    }
}

function Main {
    Write-ColorOutput "MSIX Release für Mauscribe" "Blue"
    Write-ColorOutput "================================================" "Blue"
    
    # Prüfe Voraussetzungen
    if (-not (Test-Prerequisites)) {
        Write-ColorOutput "Voraussetzungen nicht erfüllt" "Red"
        exit 1
    }
    
    # Hole Version
    $version = Get-Version
    if (-not $version) {
        Write-ColorOutput "Version konnte nicht gelesen werden" "Red"
        exit 1
    }
    
    # Bestätigung
    if (-not $Force) {
        Write-ColorOutput "`nRelease-Details:" "Cyan"
        Write-ColorOutput "   Version: $version" "White"
        Write-ColorOutput "   Tag: v$version" "White"
        Write-ColorOutput "   Branch: $(git branch --show-current)" "White"
        Write-ColorOutput ""
        
        $confirm = Read-Host "Fortfahren? (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-ColorOutput "Release abgebrochen" "Red"
            exit 0
        }
    }
    
    # Erstelle Git-Tag
    if (-not (Create-GitTag -Version $version)) {
        Write-ColorOutput "Git-Tag konnte nicht erstellt werden" "Red"
        exit 1
    }
    
    # Pushe Tag
    if (-not (Push-GitTag -Version $version)) {
        Write-ColorOutput "Tag konnte nicht gepusht werden" "Red"
        exit 1
    }
    
    # GitHub Release Info
    $repo = Get-GitHubRepo
    if ($repo) {
        Write-ColorOutput "`nGitHub Release wird automatisch erstellt..." "Blue"
        Write-ColorOutput "Überprüfen Sie: https://github.com/$repo/releases" "Cyan"
    }
    
    Write-ColorOutput "`nRelease-Prozess erfolgreich abgeschlossen!" "Green"
    Write-ColorOutput "MSIX-Paket wird automatisch von GitHub Actions erstellt" "Green"
}

# Skript ausführen
Main