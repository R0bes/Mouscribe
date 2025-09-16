# PowerShell Beispiele für Cursor-Manipulation
# Verschiedene Methoden und erweiterte Funktionen

# Beispiel 1: Temporärer Cursor-Wechsel
function Set-TemporaryCursor {
    param(
        [string]$CursorType = "Hand",
        [int]$DurationSeconds = 5
    )
    
    Write-Host "🕐 Setze temporären Cursor für $DurationSeconds Sekunden..." -ForegroundColor Yellow
    
    # Aktuellen Cursor speichern (vereinfacht)
    $originalCursor = "Arrow"
    
    # Neuen Cursor setzen
    & ".\cursor_changer.ps1" -CursorType $CursorType
    
    # Timer für automatische Wiederherstellung
    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = $DurationSeconds * 1000
    $timer.Add_Tick({
        & ".\cursor_changer.ps1" -CursorType $originalCursor
        $timer.Stop()
        $timer.Dispose()
        Write-Host "✅ Cursor automatisch wiederhergestellt" -ForegroundColor Green
    })
    
    $timer.Start()
    Write-Host "✅ Temporärer Cursor gesetzt!" -ForegroundColor Green
}

# Beispiel 2: Cursor-Animation (schneller Wechsel)
function Start-CursorAnimation {
    param(
        [string[]]$CursorSequence = @("Arrow", "Hand", "Cross", "IBeam"),
        [int]$IntervalMs = 500,
        [int]$DurationSeconds = 10
    )
    
    Write-Host "🎬 Starte Cursor-Animation..." -ForegroundColor Yellow
    
    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = $IntervalMs
    $currentIndex = 0
    $startTime = Get-Date
    
    $timer.Add_Tick({
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -ge $DurationSeconds) {
            $timer.Stop()
            $timer.Dispose()
            & ".\cursor_changer.ps1" -RestoreDefault
            Write-Host "✅ Cursor-Animation beendet" -ForegroundColor Green
            return
        }
        
        $currentCursor = $CursorSequence[$currentIndex % $CursorSequence.Length]
        & ".\cursor_changer.ps1" -CursorType $currentCursor
        $script:currentIndex++
        
        Write-Host "🔄 Cursor: $currentCursor" -ForegroundColor Cyan
    })
    
    $timer.Start()
    Write-Host "✅ Cursor-Animation gestartet!" -ForegroundColor Green
}

# Beispiel 3: Kontextabhängiger Cursor
function Set-ContextualCursor {
    param(
        [string]$Context = "Default"
    )
    
    $cursorMap = @{
        "Text" = "IBeam"
        "Link" = "Hand"
        "Wait" = "Wait"
        "Resize" = "SizeAll"
        "Move" = "SizeAll"
        "Help" = "Help"
        "Forbidden" = "No"
        "Default" = "Arrow"
    }
    
    $cursorType = $cursorMap[$Context]
    if (-not $cursorType) {
        $cursorType = "Arrow"
    }
    
    Write-Host "🎯 Setze kontextabhängigen Cursor: $Context -> $cursorType" -ForegroundColor Yellow
    & ".\cursor_changer.ps1" -CursorType $cursorType
}

# Beispiel 4: Cursor basierend auf System-Zustand
function Set-SystemStateCursor {
    param(
        [string]$State = "Normal"
    )
    
    switch ($State) {
        "Loading" {
            Write-Host "⏳ System lädt..." -ForegroundColor Yellow
            & ".\cursor_changer.ps1" -CursorType "Wait"
        }
        "Error" {
            Write-Host "❌ System-Fehler erkannt" -ForegroundColor Red
            & ".\cursor_changer.ps1" -CursorType "No"
        }
        "Success" {
            Write-Host "✅ Operation erfolgreich" -ForegroundColor Green
            & ".\cursor_changer.ps1" -CursorType "Hand"
        }
        "Help" {
            Write-Host "❓ Hilfe-Modus aktiv" -ForegroundColor Cyan
            & ".\cursor_changer.ps1" -CursorType "Help"
        }
        default {
            Write-Host "🔄 Normaler Betrieb" -ForegroundColor White
            & ".\cursor_changer.ps1" -CursorType "Arrow"
        }
    }
}

# Beispiel 5: Interaktiver Cursor-Manager
function Start-InteractiveCursorManager {
    Write-Host "🎮 Interaktiver Cursor-Manager" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "Drücke eine Taste für verschiedene Cursor:" -ForegroundColor Yellow
    Write-Host "1 - Hand Cursor" -ForegroundColor White
    Write-Host "2 - Cross Cursor" -ForegroundColor White
    Write-Host "3 - IBeam Cursor" -ForegroundColor White
    Write-Host "4 - Wait Cursor" -ForegroundColor White
    Write-Host "5 - Help Cursor" -ForegroundColor White
    Write-Host "A - Cursor-Animation starten" -ForegroundColor White
    Write-Host "R - Standard-Cursor wiederherstellen" -ForegroundColor White
    Write-Host "Q - Beenden" -ForegroundColor White
    
    do {
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        switch ($key.Character) {
            '1' { & ".\cursor_changer.ps1" -CursorType "Hand" }
            '2' { & ".\cursor_changer.ps1" -CursorType "Cross" }
            '3' { & ".\cursor_changer.ps1" -CursorType "IBeam" }
            '4' { & ".\cursor_changer.ps1" -CursorType "Wait" }
            '5' { & ".\cursor_changer.ps1" -CursorType "Help" }
            'A' { Start-CursorAnimation }
            'R' { & ".\cursor_changer.ps1" -RestoreDefault }
            'Q' { 
                Write-Host "`n👋 Auf Wiedersehen!" -ForegroundColor Green
                & ".\cursor_changer.ps1" -RestoreDefault
                break 
            }
        }
    } while ($key.Character -ne 'Q')
}

# Beispiel 6: Cursor für spezielle Anwendungen
function Set-ApplicationCursor {
    param(
        [string]$Application = "Default"
    )
    
    $appCursors = @{
        "Notepad" = "IBeam"
        "Browser" = "Hand"
        "Game" = "Cross"
        "Design" = "SizeAll"
        "Terminal" = "Arrow"
        "Default" = "Arrow"
    }
    
    $cursorType = $appCursors[$Application]
    Write-Host "📱 Setze Anwendungs-Cursor für $Application : $cursorType" -ForegroundColor Yellow
    & ".\cursor_changer.ps1" -CursorType $cursorType
}

# Hauptmenü
Write-Host "🖱️  Erweiterte Cursor-Beispiele" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verfügbare Funktionen:" -ForegroundColor Yellow
Write-Host "1. Set-TemporaryCursor -CursorType Hand -DurationSeconds 5" -ForegroundColor White
Write-Host "2. Start-CursorAnimation -DurationSeconds 10" -ForegroundColor White
Write-Host "3. Set-ContextualCursor -Context Text" -ForegroundColor White
Write-Host "4. Set-SystemStateCursor -State Loading" -ForegroundColor White
Write-Host "5. Start-InteractiveCursorManager" -ForegroundColor White
Write-Host "6. Set-ApplicationCursor -Application Browser" -ForegroundColor White
Write-Host ""
Write-Host "Beispiele ausführen:" -ForegroundColor Cyan
Write-Host "Set-TemporaryCursor -CursorType Hand -DurationSeconds 3" -ForegroundColor Green
Write-Host "Start-CursorAnimation" -ForegroundColor Green
Write-Host "Set-ContextualCursor -Context Link" -ForegroundColor Green
