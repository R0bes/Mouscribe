# MODUS-WECHSEL ANLEITUNG - MAUSCRIBE DUAL MODE SYSTEM

## 🔄 **WIE DU ZWISCHEN DEN MODI WECHSELN KANNST**

### 1. **📱 ÜBER DAS CONTROL CENTER (GUI)**

**Neuer "Mode" Tab im Control Center:**
- Öffne das Control Center über das SystemTray
- Gehe zum **"🎛️ Mode"** Tab (erster Tab)
- Wähle zwischen **"Normal Mode"** und **"Enhanced Mode"**
- Sieh dir aktuelle Statistiken und Session-Info an

**Features:**
- ✅ Visuelle Mode-Auswahl mit Beschreibungen
- ✅ Live-Statistiken (Recordings, Duration, Confidence)
- ✅ Session-Informationen
- ✅ Ein-Klick Mode-Wechsel

### 2. **💻 ÜBER DIE KOMMANDOZEILE**

**Mode Switcher Tool:**
```bash
# Aktuellen Status anzeigen
python mode_switcher.py status

# Zu Normal Mode wechseln
python mode_switcher.py switch --mode normal

# Zu Enhanced Mode wechseln
python mode_switcher.py switch --mode enhanced
```

**Features:**
- ✅ Schneller Mode-Wechsel ohne GUI
- ✅ Automatische Session-Verwaltung
- ✅ Settings.toml wird automatisch aktualisiert
- ✅ Status-Informationen

### 3. **🎯 ÜBER DAS SYSTEMTRAY (Kontextmenü)**

**Enhanced SystemTray mit Mode-Optionen:**
- Rechtsklick auf das Mauscribe-Icon im SystemTray
- Wähle **"📝 Switch to Normal Mode"** oder **"🎯 Switch to Enhanced Mode"**
- Status-Informationen über **"📊 Current Status"**

**Features:**
- ✅ Mode-Wechsel ohne Control Center öffnen
- ✅ Live-Status-Anzeige
- ✅ Integration in bestehende Workflow

### 4. **⚙️ ÜBER DIE SETTINGS.TOML**

**Manuelle Konfiguration:**
```toml
[recording_modes]
default_mode = "normal"  # oder "enhanced"
```

**Features:**
- ✅ Persistente Konfiguration
- ✅ Startet automatisch im gewählten Mode
- ✅ Wird von allen Tools respektiert

## 🎯 **MODI IM DETAIL**

### 📝 **NORMAL MODUS (Standard)**
**Für:** Normale Nutzung, Freunde, täglicher Gebrauch

**Verhalten:**
- Audio-Dateien werden nach erfolgreicher Transkription gelöscht
- Nur Transkriptionen werden temporär gespeichert
- Automatische Bereinigung nach N Aufnahmen oder Programmende
- Minimaler Speicherverbrauch

**Vorteile:**
- ✅ Schnell und effizient
- ✅ Keine Speicherprobleme
- ✅ Perfekt für Freunde
- ✅ Automatische Bereinigung

### 🎯 **ENHANCED MODUS (Training)**
**Für:** Training-Daten, ML-Entwicklung, Stimmtraining

**Verhalten:**
- Audio-Dateien + Transkriptionen werden dauerhaft gespeichert
- Erweiterte Metadaten (Modell, Confidence, Word-Timestamps)
- Training-Daten Management
- Session-basierte Organisation

**Vorteile:**
- ✅ Vollständige Historie für Stimmtraining
- ✅ Erweiterte Metadaten für ML
- ✅ Flexible Datenorganisation
- ✅ Quality Scoring

## 🚀 **PRAKTISCHE ANWENDUNG**

### **Für normale Nutzung:**
```bash
# Starte in Normal Mode
python mode_switcher.py switch --mode normal
python main.py
```

### **Für Training-Sessions:**
```bash
# Starte in Enhanced Mode
python mode_switcher.py switch --mode enhanced
python main.py
# ... mehrere Stunden aufnehmen ...
# Alle Daten werden für Training gespeichert
```

### **Mode-Wechsel während der Nutzung:**
```bash
# Wechsle zu Enhanced Mode für wichtige Aufnahmen
python mode_switcher.py switch --mode enhanced
# ... wichtige Aufnahmen machen ...
# Zurück zu Normal Mode
python mode_switcher.py switch --mode normal
```

## 📊 **STATISTIKEN UND MONITORING**

### **Session-Informationen:**
- **Session ID**: Eindeutige Identifikation jeder Session
- **Recording Count**: Anzahl Aufnahmen in aktueller Session
- **Total Duration**: Gesamtdauer aller Aufnahmen
- **Average Confidence**: Durchschnittliche Transkriptions-Qualität

### **Training Data Management:**
- **Auto-Marking**: Automatisches Markieren bei hoher Confidence (≥0.8)
- **Quality Scoring**: Manuelle Qualitätsbewertung
- **Domain Tagging**: Kategorisierung nach Bereichen
- **Speaker Identification**: Multi-Speaker Support

## 🎮 **INTEGRATION IN MAUSCRIBE**

### **Automatische Features:**
- **Mode-Detection**: App erkennt aktuellen Mode beim Start
- **Session-Management**: Automatische Session-Verwaltung
- **Cleanup**: Automatische Bereinigung in Normal Mode
- **Event-System**: Live-Updates zwischen Modi

### **Control Center Integration:**
- **Mode Tab**: Visuelle Mode-Auswahl
- **Status Tab**: Live-Mode-Anzeige
- **Audio Tab**: Mode-spezifische Audio-Verwaltung
- **Logs Tab**: Mode-Wechsel-Logging

## ✅ **ZUSAMMENFASSUNG**

**Du kannst zwischen den Modi wechseln über:**
1. **Control Center GUI** - Visuell und benutzerfreundlich
2. **Kommandozeile** - Schnell und scriptbar
3. **SystemTray** - Integriert in bestehende Workflow
4. **Settings.toml** - Persistente Konfiguration

**Die neue Architektur unterstützt:**
- ✅ **Normal Mode** für tägliche Nutzung
- ✅ **Enhanced Mode** für Training-Daten
- ✅ **Automatische Session-Verwaltung**
- ✅ **Live Mode-Wechsel**
- ✅ **Comprehensive Statistics**

**Perfekt für deine Anwendung:**
- **Freunde** nutzen Normal Mode (minimaler Speicher)
- **Du** nutzt Enhanced Mode für Training-Daten
- **Flexibler Wechsel** je nach Bedarf

**Die Implementierung ist vollständig und getestet!** 🎉✨
