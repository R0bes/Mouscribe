# PowerShell Script - Animierte Maus über Taskleiste
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Maus-Form erstellen
$form = New-Object System.Windows.Forms.Form
$form.Text = "Mouse Walker"
$form.Size = New-Object System.Drawing.Size(50, 50)
$form.StartPosition = "Manual"
$form.FormBorderStyle = "None"
$form.BackColor = [System.Drawing.Color]::Magenta
$form.TransparencyKey = [System.Drawing.Color]::Magenta
$form.TopMost = $true
$form.ShowInTaskbar = $false

# Maus-Label mit Emoji
$label = New-Object System.Windows.Forms.Label
$label.Text = "🐭"
$label.Font = New-Object System.Drawing.Font("Segoe UI Emoji", 30)
$label.Size = New-Object System.Drawing.Size(50, 50)
$label.Location = New-Object System.Drawing.Point(0, 0)
$form.Controls.Add($label)

# Bildschirm-Infos abrufen
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$screenWidth = $screen.WorkingArea.Width
$screenHeight = $screen.Bounds.Height
$taskbarHeight = $screen.Bounds.Height - $screen.WorkingArea.Height

# Startposition (links über der Taskleiste)
$currentX = -50
$yPosition = $screenHeight - $taskbarHeight - 60

# Timer für Animation
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 20  # Update alle 20ms
$direction = 1  # 1 = rechts, -1 = links
$speed = 3

$timer.Add_Tick({
    $script:currentX += ($speed * $script:direction)
    
    # Richtung wechseln an den Rändern
    if ($script:currentX -gt $screenWidth) {
        $script:direction = -1
        $label.Text = "🐭"  # Maus schaut nach links
    }
    elseif ($script:currentX -lt -50) {
        $script:direction = 1
        $label.Text = "🐭"  # Maus schaut nach rechts
    }
    
    # Position aktualisieren
    $form.Location = New-Object System.Drawing.Point($script:currentX, $yPosition)
})

# ESC-Taste zum Beenden
$form.Add_KeyDown({
    if ($_.KeyCode -eq "Escape") {
        $timer.Stop()
        $form.Close()
    }
})

# Klick zum Beenden
$form.Add_Click({
    $timer.Stop()
    $form.Close()
})

$label.Add_Click({
    $timer.Stop()
    $form.Close()
})

# Starten
$form.Show()
$timer.Start()

# Message Loop
[System.Windows.Forms.Application]::Run($form)

# Aufräumen
$timer.Dispose()
$form.Dispose()