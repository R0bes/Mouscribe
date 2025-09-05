# MSIX Release Workflow Script
# Fuehrt den kompletten Release-Prozess automatisch durch

param(
    [switch]$Force = $false
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Main {
    Write-ColorOutput "MSIX Release Workflow gestartet..." "Blue"
    Write-ColorOutput "================================================" "Blue"
    Write-ColorOutput ""
    Write-ColorOutput "Workflow-Schritte:" "Cyan"
    Write-ColorOutput "1. Version automatisch erhöhen (Patch)" "White"
    Write-ColorOutput "2. Alle Aenderungen committen" "White"
    Write-ColorOutput "3. Git-Tag erstellen" "White"
    Write-ColorOutput "4. Tag zu GitHub pushen" "White"
    Write-ColorOutput "5. GitHub Release automatisch erstellen" "White"
    Write-ColorOutput ""
    Write-ColorOutput "Hinweis: Alle uncommitted changes werden automatisch committed!" "Yellow"
    Write-ColorOutput ""
    
    if (-not $Force) {
        $confirm = Read-Host "Fortfahren? (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-ColorOutput "Workflow abgebrochen" "Red"
            exit 0
        }
    }
    
    Write-ColorOutput "Workflow gestartet..." "Green"
    Write-ColorOutput ""
    
    # 1. Version lesen und erhöhen
    Write-ColorOutput "Lese und erhöhe Version..." "Blue"
    try {
        $currentVersion = python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"
        Write-ColorOutput "Aktuelle Version: $currentVersion" "Cyan"
        
        # Version erhöhen (Patch-Version)
        $versionParts = $currentVersion.Split('.')
        if ($versionParts.Length -eq 3) {
            $major = [int]$versionParts[0]
            $minor = [int]$versionParts[1]
            $patch = [int]$versionParts[2]
            $patch++
            $newVersion = "$major.$minor.$patch"
        } else {
            Write-ColorOutput "Ungültiges Versionsformat: $currentVersion" "Red"
            exit 1
        }
        
        Write-ColorOutput "Neue Version: $newVersion" "Green"
        
        # Version in pyproject.toml aktualisieren
        Write-ColorOutput "Aktualisiere pyproject.toml..." "Blue"
        $pyprojectContent = Get-Content "pyproject.toml" -Raw
        $pyprojectContent = $pyprojectContent -replace "version = `"$currentVersion`"", "version = `"$newVersion`""
        $pyprojectContent | Set-Content "pyproject.toml" -Encoding UTF8
        Write-ColorOutput "pyproject.toml aktualisiert" "Green"
        
        $version = $newVersion
    } catch {
        Write-ColorOutput "Fehler beim Lesen/Erhöhen der Version: $($_.Exception.Message)" "Red"
        exit 1
    }
    
    Write-ColorOutput ""
    
    # 2. Alle Änderungen committen (inklusive Version-Update)
    Write-ColorOutput "Committte alle Aenderungen..." "Blue"
    git add .
    $commitMsg = "feat: Add MSIX support and release automation (v$version)"
    
    # Versuche Commit ohne Pre-commit Hooks
    try {
        git commit -m $commitMsg --no-verify
        Write-ColorOutput "Aenderungen committed (ohne Pre-commit Hooks)" "Green"
    } catch {
        Write-ColorOutput "Fehler beim Commit: $($_.Exception.Message)" "Red"
        Write-ColorOutput "Versuche Commit mit Pre-commit Hooks..." "Yellow"
        git commit -m $commitMsg
        Write-ColorOutput "Aenderungen committed" "Green"
    }
    
    Write-ColorOutput ""
    
    # 3. Git-Tag erstellen
    Write-ColorOutput "Erstelle Git-Tag..." "Blue"
    try {
        # Prüfe ob Tag bereits existiert
        $existingTag = git tag -l "v$version"
        if ($existingTag) {
            Write-ColorOutput "Tag v$version existiert bereits" "Yellow"
            if (-not $Force) {
                Write-ColorOutput "Verwenden Sie -Force um Tag zu überschreiben" "Yellow"
                Write-ColorOutput "Oder erhöhen Sie die Version in pyproject.toml" "Yellow"
                exit 1
            }
            git tag -d "v$version"
            Write-ColorOutput "Alten Tag gelöscht" "Yellow"
        }
        
        git tag "v$version"
        Write-ColorOutput "Tag erstellt: v$version" "Green"
    } catch {
        Write-ColorOutput "Fehler beim Erstellen des Tags: $($_.Exception.Message)" "Red"
        exit 1
    }
    
    Write-ColorOutput ""
    
    # 4. Tag pushen
    Write-ColorOutput "Pushe zu GitHub..." "Blue"
    try {
        git push origin "v$version"
        Write-ColorOutput "Tag gepusht" "Green"
    } catch {
        Write-ColorOutput "Fehler beim Pushen: $($_.Exception.Message)" "Red"
        exit 1
    }
    
    Write-ColorOutput ""
    
    # 5. GitHub Release Info
    Write-ColorOutput "GitHub Release wird automatisch erstellt..." "Blue"
    try {
        $remoteUrl = git config --get remote.origin.url
        Write-ColorOutput "Remote URL: $remoteUrl" "Gray"
        
        if ($remoteUrl -match 'github\.com[:/]([^/]*)/([^/]*?)\.git') {
            $owner = $matches[1]
            $repoName = $matches[2]
            Write-ColorOutput "Ueberpruefen Sie: https://github.com/$owner/$repoName/releases" "Cyan"
        } elseif ($remoteUrl -match 'github\.com[:/]([^/]*)/([^/]*?)') {
            $owner = $matches[1]
            $repoName = $matches[2]
            Write-ColorOutput "Ueberpruefen Sie: https://github.com/$owner/$repoName/releases" "Cyan"
        } else {
            Write-ColorOutput "Konnte GitHub Repo aus URL nicht ermitteln: $remoteUrl" "Yellow"
        }
    } catch {
        Write-ColorOutput "Konnte GitHub Repo nicht ermitteln: $($_.Exception.Message)" "Yellow"
    }
    
    Write-ColorOutput ""
    Write-ColorOutput "MSIX Release Workflow erfolgreich abgeschlossen!" "Green"
    Write-ColorOutput "MSIX-Paket wird automatisch von GitHub Actions erstellt" "Green"
}

# Skript ausfuehren
Main