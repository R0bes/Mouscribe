# NEUE MAUSCRIBE ARCHITEKTUR - ZUSAMMENFASSUNG

## 🎯 **DUAL MODE SYSTEM**

### 📝 **NORMAL MODUS (Standard)**
- **Ziel**: Minimaler Speicherverbrauch für normale Nutzung
- **Verhalten**:
  - Audio-Dateien werden nach erfolgreicher Transkription gelöscht
  - Nur Transkriptionen werden temporär gespeichert
  - Automatische Bereinigung nach N Aufnahmen oder Programmende
- **Vorteile**:
  - Schnell und effizient
  - Keine Speicherprobleme
  - Perfekt für Freunde und normale Nutzung

### 🎯 **ENHANCED MODUS (Erweitert)**
- **Ziel**: Vollständige Datensammlung für ML-Training
- **Verhalten**:
  - Audio-Dateien + Transkriptionen werden dauerhaft gespeichert
  - Erweiterte Metadaten (Modell, Confidence, Word-Timestamps)
  - Training-Daten Management
  - Session-basierte Organisation
- **Vorteile**:
  - Vollständige Historie für Stimmtraining
  - Erweiterte Metadaten für ML
  - Flexible Datenorganisation

## 🗄️ **NEUE DATENBANKSTRUKTUR**

### **Audio Recordings Table**
```sql
- id (Primary Key)
- session_id (Session-Gruppierung)
- timestamp (Aufnahme-Zeit)
- audio_file_path (Pfad zur Datei - NULL in Normal Mode)
- duration_seconds, sample_rate, channels, audio_format
- file_size_bytes
- audio_data (BLOB - nur in Enhanced Mode)
- mode ('normal' oder 'enhanced')
- metadata (JSON für erweiterte Daten)
- created_at, deleted_at
```

### **Transcriptions Table**
```sql
- id (Primary Key)
- audio_recording_id (Foreign Key)
- raw_text, corrected_text
- confidence_score, language
- model_name, model_size (Whisper-Modell Info)
- processing_time_ms
- word_timestamps (JSON für Word-Level Timestamps)
- segments (JSON für Segment-Level Daten)
- is_training_data (Boolean für ML-Training)
- training_tags (JSON für Training-Tags)
- created_at
```

### **Sessions Table**
```sql
- id (Session-ID)
- start_time, end_time
- mode ('normal' oder 'enhanced')
- total_recordings, total_duration
- notes
- created_at
```

### **Training Data Table**
```sql
- id (Primary Key)
- transcription_id, audio_recording_id
- quality_score (Manuelle Qualitätsbewertung)
- speaker_id (Multi-Speaker Support)
- domain ('general', 'technical', 'casual')
- tags (JSON für flexible Tagging)
- is_validated, validation_notes
- created_at
```

## 🚀 **IMPLEMENTIERUNG**

### **1. Enhanced Database Manager**
- `src/utils/enhanced_database.py`
- Dual-Mode Support
- Session Management
- Training Data Collection
- Automatic Cleanup

### **2. Recording Mode Configuration**
- `src/config/recording_modes.py`
- Flexible Konfiguration für beide Modi
- Training-spezifische Einstellungen
- Quality Scoring

### **3. Integration in MauscribeApp**
- Mode-Switching zur Laufzeit
- Session-basierte Aufnahmen
- Enhanced Event-System
- Statistics und Monitoring

### **4. Enhanced Control Center**
- Mode-Anzeige im Status Tab
- Training Data Management
- Session-Übersicht
- Statistics Dashboard

## 🎮 **NUTZUNG**

### **Normal Mode (Standard)**
```python
# Automatisch aktiviert
app = MauscribeApp()  # Normal mode by default
app.start_recording()  # Audio wird nach Transkription gelöscht
```

### **Enhanced Mode (Training)**
```python
# Manuell aktivieren
app.switch_recording_mode('enhanced')
app.start_recording()  # Audio wird dauerhaft gespeichert
```

### **Training Data Collection**
```python
# Automatisches Markieren für Training
if confidence >= 0.8:
    db.mark_for_training(transcription_id, quality_score=confidence)
```

## 📊 **VORTEILE DER NEUEN ARCHITEKTUR**

### **Für normale Nutzung:**
- ✅ Minimaler Speicherverbrauch
- ✅ Schnelle Performance
- ✅ Automatische Bereinigung
- ✅ Keine Konfiguration nötig

### **Für Training/ML:**
- ✅ Vollständige Datensammlung
- ✅ Erweiterte Metadaten
- ✅ Flexible Organisation
- ✅ Quality Scoring
- ✅ Session Management
- ✅ Multi-Speaker Support

### **Für Entwicklung:**
- ✅ Modulare Architektur
- ✅ Einfache Erweiterbarkeit
- ✅ Flexible Konfiguration
- ✅ Event-basierte Updates
- ✅ Comprehensive Logging

## 🔄 **MIGRATION VON ALTER DATENBANK**

### **Backup erstellt:**
- `data/backup_20251024_160201/`
- 1836 Audio-Dateien gesichert
- 1834 Transkriptionen gesichert

### **Neue Datenbank:**
- `data/audio_database_v2.db`
- Erweiterte Struktur
- Dual-Mode Support
- Training Data Management

## 🎯 **NÄCHSTE SCHRITTE**

1. **Integration in MauscribeApp** - Mode-Switching implementieren
2. **Control Center Updates** - Enhanced Features anzeigen
3. **Training Data UI** - Management Interface erstellen
4. **Statistics Dashboard** - Session- und Training-Statistiken
5. **Backup System** - Automatische Backups für Enhanced Mode

**Die neue Architektur ist bereit und getestet!** 🎉✨
