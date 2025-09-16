# PowerShell Test-Skript für Cursor-Funktionalität
# Testet verschiedene Cursor-Änderungen

Write-Host "🧪 Cursor Test Suite" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Test 1: Verfügbare Cursor anzeigen
Write-Host "`n📋 Test 1: Verfügbare Cursor anzeigen" -ForegroundColor Yellow
& ".\cursor_changer.ps1" -ShowAvailableCursors

Start-Sleep -Seconds 2

# Test 2: Verschiedene Cursor-Typen testen
$testCursors = @("Hand", "Cross", "IBeam", "Wait", "Help")

foreach ($cursor in $testCursors) {
    Write-Host "`n🔄 Test: Cursor ändern zu $cursor" -ForegroundColor Yellow
    & ".\cursor_changer.ps1" -CursorType $cursor
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $cursor erfolgreich angewendet" -ForegroundColor Green
    } else {
        Write-Host "❌ Fehler bei $cursor" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

# Test 3: Standard-Cursor wiederherstellen
Write-Host "`n🔄 Test: Standard-Cursor wiederherstellen" -ForegroundColor Yellow
& ".\cursor_changer.ps1" -RestoreDefault

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Standard-Cursor erfolgreich wiederhergestellt" -ForegroundColor Green
} else {
    Write-Host "❌ Fehler beim Wiederherstellen" -ForegroundColor Red
}

# Test 4: Benutzerdefinierten Cursor erstellen und testen
Write-Host "`n🔄 Test: Benutzerdefinierten Cursor erstellen" -ForegroundColor Yellow
& ".\cursor_changer.ps1" -CursorType Custom

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Benutzerdefinierter Cursor erfolgreich erstellt und angewendet" -ForegroundColor Green
} else {
    Write-Host "❌ Fehler beim Erstellen des benutzerdefinierten Cursors" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Abschließend Standard wiederherstellen
Write-Host "`n🔄 Abschließende Wiederherstellung der Standard-Cursor" -ForegroundColor Yellow
& ".\cursor_changer.ps1" -RestoreDefault

Write-Host "`n🎉 Alle Tests abgeschlossen!" -ForegroundColor Green
Write-Host "💡 Du kannst das Skript auch manuell verwenden:" -ForegroundColor Cyan
Write-Host "   .\cursor_changer.ps1 -CursorType Hand" -ForegroundColor White
Write-Host "   .\cursor_changer.ps1 -RestoreDefault" -ForegroundColor White
