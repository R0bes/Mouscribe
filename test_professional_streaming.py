#!/usr/bin/env python3
"""
Professionelle Streaming-Lösung für Kato Agent System
- Sliding Window Analyse
- Überlappende Zusammensetzung
- Streaming-Verarbeitung
- Hintergrund-Analyse
- Echtzeit-Antworten
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from collections import deque
from typing import Optional, Callable, List, Dict, Any
import queue
import logging
import sys
import pyperclip
import re

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfessionalStreamingAgent:
    """Professioneller Streaming-Agent mit Sliding Window Analyse."""
    
    def __init__(self):
        self.running = False
        self.hotword_model = None
        self.transcription_model = None
        
        # Kato Agent System
        self.wake_words = ["kato", "hey kato", "okay kato"]
        self.start_words = ["start"]
        self.stop_words = ["stopp", "stop"]
        self.exit_words = ["beenden", "exit"]
        self.insert_words = ["einfügen", "insert", "paste"]
        
        # State Management
        self.wake_word_detected = False
        self.command_pending = False
        self.is_recording = False
        
        # Professional Streaming Components
        self.audio_buffer = deque(maxlen=96000)  # 6 Sekunden bei 16kHz
        self.sliding_window_size = 32000  # 2 Sekunden
        self.overlap_size = 8000  # 0.5 Sekunden Überlappung
        self.recording_buffer = []
        self.recording_start_time = 0.0
        
        # Background Analysis
        self.analysis_queue = queue.Queue()
        self.background_thread = None
        self.realtime_responses = []
        
        # Streaming State
        self.current_window = np.array([])
        self.window_position = 0
        self.last_analysis_time = 0
        
    def _load_models(self) -> bool:
        """Lade Whisper Modelle."""
        try:
            # Verwende größeres Modell für bessere Hot Word Erkennung
            self.hotword_model = WhisperModel("small", device="cpu", compute_type="float32")
            logger.info("✅ Hot Word Modell geladen (small - verbessert)")
            self.transcription_model = WhisperModel("medium", device="cpu", compute_type="float32")
            logger.info("✅ Transkriptions-Modell geladen (medium - verbessert)")
            return True
        except Exception as e:
            logger.error(f"❌ Whisper Modell Fehler: {e}")
            return False
    
    def start(self):
        """Starte den professionellen Streaming-Agent."""
        if self.running:
            logger.warning("⚠️ Agent läuft bereits")
            return

        logger.info("🚀 Starte professionellen Streaming-Agent...")
        if not self._load_models():
            return

        self.running = True
        
        # Starte Background Analysis Thread
        self.background_thread = threading.Thread(target=self._background_analysis_loop, daemon=True)
        self.background_thread.start()
        
        # Starte Audio Streaming Thread
        self.audio_thread = threading.Thread(target=self._professional_audio_loop, daemon=True)
        self.audio_thread.start()
        
        logger.info("✅ Professioneller Streaming-Agent läuft")
    
    def stop(self):
        """Stoppe den Agent."""
        if not self.running:
            return
        
        logger.info("🛑 Stoppe professionellen Streaming-Agent...")
        self.running = False
        
        if self.background_thread:
            self.background_thread.join(timeout=5)
        if self.audio_thread:
            self.audio_thread.join(timeout=5)
            
        logger.info("✅ Professioneller Streaming-Agent gestoppt")
    
    def _professional_audio_loop(self):
        """Professionelle Audio-Loop mit Sliding Window."""
        logger.info("🔄 Professionelle Audio-Loop gestartet")
        
        duration = 3.0  # 3 Sekunden Chunks für bessere Hot Word Erkennung
        sample_rate = 16000
        
        while self.running:
            try:
                # Audio aufnehmen
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype=np.float32,
                    blocking=True
                )
                
                if audio_data is not None and len(audio_data) > 0:
                    audio_flat = audio_data.flatten()
                    
                    # Audio zu Sliding Window hinzufügen
                    self._update_sliding_window(audio_flat)
                    
                    # Hot Word Detection
                    self._check_hot_words(audio_flat)
                    
                    # Wenn Aufnahme läuft, zu Recording Buffer hinzufügen
                    if self.is_recording:
                        self.recording_buffer.append(audio_data.copy())
                        logger.debug(f"📝 Aufnahme läuft: {len(self.recording_buffer)} Segmente")
                    
                    # Background Analysis für aktuelles Window
                    self._trigger_background_analysis()
                    
            except Exception as e:
                logger.error(f"❌ Audio-Loop Fehler: {e}")
            
            time.sleep(0.05)  # 50ms für bessere Responsivität
    
    def _update_sliding_window(self, audio_data: np.ndarray):
        """Update Sliding Window mit neuem Audio."""
        # Füge neues Audio zum Buffer hinzu
        self.audio_buffer.extend(audio_data)
        
        # Erstelle aktuelles Window
        if len(self.audio_buffer) >= self.sliding_window_size:
            # Nimm die letzten sliding_window_size Samples
            self.current_window = np.array(list(self.audio_buffer)[-self.sliding_window_size:])
            self.window_position = len(self.audio_buffer) - self.sliding_window_size
        else:
            # Wenn Buffer noch nicht voll, nimm alles
            self.current_window = np.array(list(self.audio_buffer))
            self.window_position = 0
    
    def _trigger_background_analysis(self):
        """Triggere Background Analysis für aktuelles Window."""
        current_time = time.time()
        
        # Analysiere alle 0.5 Sekunden
        if current_time - self.last_analysis_time > 0.5:
            if len(self.current_window) > 0:
                # Prüfe ob Audio laut genug ist
                if np.max(np.abs(self.current_window)) > 0.01:
                    # Füge zur Analysis Queue hinzu
                    self.analysis_queue.put({
                        'audio': self.current_window.copy(),
                        'timestamp': current_time,
                        'window_position': self.window_position
                    })
            
            self.last_analysis_time = current_time
    
    def _background_analysis_loop(self):
        """Background Analysis Loop für kontinuierliche Verarbeitung."""
        logger.info("🔄 Background Analysis Loop gestartet")
        
        while self.running:
            try:
                # Warte auf Audio-Daten in der Queue
                if not self.analysis_queue.empty():
                    analysis_data = self.analysis_queue.get(timeout=1.0)
                    
                    # Führe Background Analysis durch
                    self._analyze_audio_window(analysis_data)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Background Analysis Fehler: {e}")
    
    def _analyze_audio_window(self, analysis_data: Dict[str, Any]):
        """Analysiere Audio Window für Echtzeit-Erkenntnisse."""
        try:
            audio = analysis_data['audio']
            timestamp = analysis_data['timestamp']
            
            # Audio normalisieren
            if np.max(np.abs(audio)) > 0:
                max_val = np.max(np.abs(audio))
                if max_val > 0.1:
                    audio = audio / max_val * 0.95
            
            # Verbesserte Whisper Transkription für Background Analysis
            segments, info = self.hotword_model.transcribe(
                audio=audio,
                language="de",
                vad_filter=True,  # Voice Activity Detection aktiviert
                beam_size=3,      # Mehr Beam Search für bessere Erkennung
                best_of=3,        # Mehr Kandidaten für bessere Erkennung
                temperature=0.0,  # Deterministisch
                condition_on_previous_text=False,  # Keine Abhängigkeit von vorherigem Text
            )
            
            text_parts = [seg.text.strip() for seg in segments]
            text = " ".join([t for t in text_parts if t]).lower().strip()
            
            if text:
                logger.info(f"🔍 Background Analysis: '{text}'")
                
                # Speichere für Echtzeit-Antworten
                self.realtime_responses.append({
                    'text': text,
                    'timestamp': timestamp,
                    'confidence': info.language_probability if hasattr(info, 'language_probability') else 0.5
                })
                
                # Behalte nur die letzten 10 Antworten
                if len(self.realtime_responses) > 10:
                    self.realtime_responses.pop(0)
        
        except Exception as e:
            logger.error(f"❌ Audio Window Analysis Fehler: {e}")
    
    def _check_hot_words(self, audio_data: np.ndarray):
        """Prüfe auf Hot Words mit verbesserter Logik."""
        try:
            # Audio normalisieren
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
            
            # Verbesserte Whisper Transkription für bessere Erkennung
            segments, info = self.hotword_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=True,  # Voice Activity Detection aktiviert
                beam_size=5,      # Mehr Beam Search für bessere Erkennung
                best_of=5,        # Mehr Kandidaten für bessere Erkennung
                temperature=0.0,  # Deterministisch
                condition_on_previous_text=False,  # Keine Abhängigkeit von vorherigem Text
            )
            
            text_parts = [seg.text.strip() for seg in segments]
            text = " ".join([t for t in text_parts if t]).lower().strip()
            
            if text:
                logger.info(f"🎤 Audio erkannt: '{text}'")
                
                # Prüfe auf Wake Word + Kommando
                self._process_wake_word_command(text)
            else:
                logger.debug("🔇 Stille erkannt")
                
        except Exception as e:
            logger.error(f"❌ Hot Word Check Fehler: {e}")
    
    def _process_wake_word_command(self, text: str):
        """Verarbeite Wake Word + Kommando Pattern mit verbesserter Erkennung."""
        text_lower = text.lower()
        
        # Verbesserte Wake Word Erkennung mit Fuzzy Matching
        detected_wake_word = self._fuzzy_wake_word_detection(text_lower)
        
        if detected_wake_word:
            logger.info(f"🎯 Wake Word '{detected_wake_word}' erkannt!")
            self.wake_word_detected = True
            self.command_pending = True
            
            # Extrahiere das Kommando nach dem Wake Word
            wake_word_pos = text_lower.find(detected_wake_word)
            command_text = text_lower[wake_word_pos + len(detected_wake_word):].strip()
            
            logger.info(f"📝 Kommando-Text: '{command_text}'")
            
            # Prüfe auf Kommandos
            self._check_command(command_text)
            
        elif self.command_pending:
            # Wenn Wake Word bereits erkannt, prüfe nur auf Kommandos
            logger.info(f"📝 Kommando-Text (ohne Wake Word): '{text_lower}'")
            self._check_command(text_lower)
        else:
            # Kein Wake Word erkannt - ignoriere
            logger.debug("🔇 Kein Wake Word erkannt - ignoriere")
    
    def _fuzzy_wake_word_detection(self, text: str) -> Optional[str]:
        """Fuzzy Wake Word Detection für bessere Erkennung."""
        # Direkte Matches
        for wake_word in self.wake_words:
            if wake_word in text:
                return wake_word
        
        # Fuzzy Matches für häufige Erkennungsfehler
        fuzzy_patterns = {
            "kato": ["kartel", "kartour", "kanzo", "karto", "kato", "katost", "katostar"],
            "hey kato": ["hey kartel", "hey kartour", "hey karto"],
            "okay kato": ["okay kartel", "okay kartour", "okay karto"]
        }
        
        for wake_word, patterns in fuzzy_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    logger.info(f"🔍 Fuzzy Match: '{pattern}' → '{wake_word}'")
                    return wake_word
        
        return None
    
    def _check_command(self, command_text: str):
        """Prüfe auf spezifische Kommandos mit verbesserter Erkennung."""
        # Verbesserte Kommando-Erkennung mit Fuzzy Matching
        
        # Start Kommando mit Fuzzy Matching
        start_patterns = ["start", "stark", "stahl", "starten", "starte"]
        for pattern in start_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Start Fuzzy Match: '{pattern}' → 'start'")
                self._on_start_word_found("start", command_text)
                self._reset_wake_word_state()
                return
        
        # Stop Kommando mit Fuzzy Matching
        stop_patterns = ["stopp", "stop", "stoppen", "stoppe", "halt", "halte"]
        for pattern in stop_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Stop Fuzzy Match: '{pattern}' → 'stopp'")
                self._on_stop_word_found("stopp", command_text)
                self._reset_wake_word_state()
                return
        
        # Exit Kommando mit Fuzzy Matching
        exit_patterns = ["beenden", "beende", "exit", "ende", "schließen", "quit"]
        for pattern in exit_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Exit Fuzzy Match: '{pattern}' → 'beenden'")
                self._on_exit_word_found("beenden", command_text)
                self._reset_wake_word_state()
                return
        
        # Insert Kommando mit Fuzzy Matching
        insert_patterns = ["einfügen", "einfüge", "insert", "paste", "fügen", "füge"]
        for pattern in insert_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Insert Fuzzy Match: '{pattern}' → 'einfügen'")
                self._on_insert_word_found("einfügen", command_text)
                self._reset_wake_word_state()
                return
        
        # Kein gültiges Kommando erkannt
        logger.warning(f"⚠️ Kein gültiges Kommando in '{command_text}' erkannt")
        self._reset_wake_word_state()
    
    def _reset_wake_word_state(self):
        """Reset Wake Word State."""
        self.wake_word_detected = False
        self.command_pending = False
        logger.debug("🔄 Wake Word State zurückgesetzt")
    
    def _on_start_word_found(self, word: str, text: str):
        """Start Word gefunden."""
        logger.info(f"🎯 Start Word erkannt: '{word}' in '{text}'")
        self.start_recording()
        logger.info("✅ Start Word verarbeitet - Streaming läuft weiter")
    
    def _on_stop_word_found(self, word: str, text: str):
        """Stop Word gefunden."""
        logger.info(f"🛑 Stop Word erkannt: '{word}' in '{text}'")
        self.stop_recording()
    
    def _on_exit_word_found(self, word: str, text: str):
        """Exit Word gefunden."""
        logger.info(f"🚪 Exit Word erkannt: '{word}' in '{text}'")
        logger.info("🛑 Beende Programm...")
        self.running = False
        import os
        os._exit(0)
    
    def _on_insert_word_found(self, word: str, text: str):
        """Insert Word gefunden - füge Clipboard-Inhalt ein."""
        logger.info(f"📋 Insert Word erkannt: '{word}' in '{text}'")
        self._insert_clipboard_content()
    
    def _insert_clipboard_content(self):
        """Füge Clipboard-Inhalt ein."""
        try:
            import pyperclip
            import pyautogui
            
            clipboard_text = pyperclip.paste()
            
            if clipboard_text:
                logger.info(f"📋 Clipboard-Inhalt: '{clipboard_text}'")
                pyautogui.hotkey('ctrl', 'v')
                logger.info("✅ Clipboard-Inhalt eingefügt!")
            else:
                logger.warning("⚠️ Clipboard ist leer")
                
        except ImportError:
            logger.error("❌ pyautogui nicht verfügbar - kann nicht einfügen")
        except Exception as e:
            logger.error(f"❌ Fehler beim Einfügen: {e}")
    
    def start_recording(self):
        """Starte Aufnahme."""
        if self.is_recording:
            logger.warning("⚠️ Aufnahme läuft bereits - ignoriere")
            return
            
        logger.info("🎙️ Starte Aufnahme...")
        self.is_recording = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        logger.info("✅ Aufnahme gestartet - Streaming läuft weiter")
    
    def stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording:
            return

        logger.info("🛑 Stoppe Aufnahme...")
        self.is_recording = False

        if self.recording_buffer:
            logger.info(f"📊 Recording Buffer: {len(self.recording_buffer)} Segmente")
            
            # Professionelle Audio-Zusammensetzung mit Überlappung
            full_audio = self._professional_audio_composition()
            duration = time.time() - self.recording_start_time

            logger.info(f"📊 Aufnahme abgeschlossen:")
            logger.info(f"   - Dauer: {duration:.1f}s")
            logger.info(f"   - Samples: {len(full_audio)}")
            logger.info(f"   - Segmente: {len(self.recording_buffer)}")

            self._transcribe_recording(full_audio)
        else:
            logger.warning("⚠️ Keine Audio-Daten gesammelt")
    
    def _professional_audio_composition(self) -> np.ndarray:
        """Professionelle Audio-Zusammensetzung mit Überlappung."""
        if not self.recording_buffer:
            return np.array([])
        
        if len(self.recording_buffer) == 1:
            return self.recording_buffer[0].flatten()
        
        # Überlappende Zusammensetzung mit Crossfade
        overlap_samples = 4000  # 0.25 Sekunden bei 16kHz
        result = []
        
        for i, segment in enumerate(self.recording_buffer):
            segment_flat = segment.flatten()
            
            if i == 0:
                # Erstes Segment komplett hinzufügen
                result.append(segment_flat)
            else:
                # Überlappung mit Crossfade
                if len(result) > 0 and len(segment_flat) >= overlap_samples:
                    # Letzte overlap_samples des vorherigen Segments
                    prev_tail = result[-1][-overlap_samples:]
                    # Erste overlap_samples des aktuellen Segments
                    curr_head = segment_flat[:overlap_samples]
                    
                    # Crossfade (sanfter Übergang)
                    fade_out = np.linspace(1, 0, overlap_samples)
                    fade_in = np.linspace(0, 1, overlap_samples)
                    
                    crossfade = prev_tail * fade_out + curr_head * fade_in
                    
                    # Ersetze das Ende des vorherigen Segments
                    result[-1] = np.concatenate([result[-1][:-overlap_samples], crossfade])
                    
                    # Füge den Rest des aktuellen Segments hinzu
                    result.append(segment_flat[overlap_samples:])
                else:
                    result.append(segment_flat)
        
        return np.concatenate(result)
    
    def _transcribe_recording(self, audio_data: np.ndarray):
        """Transkribiere Aufnahme mit professionellem Modell."""
        try:
            logger.info("🎯 Starte professionelle Transkription...")
            
            # Audio normalisieren
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
            
            # Professionelle Whisper Transkription
            segments, info = self.transcription_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=False,
                beam_size=5,
                best_of=5,
                temperature=0.0,
            )
            
            segments_list = list(segments)
            logger.info(f"📊 Whisper Segmente: {len(segments_list)}")
            
            # Text zusammenfügen und bereinigen
            text_parts = [seg.text.strip() for seg in segments_list]
            full_text = " ".join([t for t in text_parts if t]).strip()
            
            # Professionelle Text-Bereinigung
            full_text = self._clean_transcription_text(full_text)
            
            if full_text:
                logger.info("✅ Professionelle Transkription erfolgreich:")
                logger.info(f"📝 Vollständiger Text: '{full_text}'")
                logger.info(f"📊 Transkriptions-Info: {info.duration:.1f}s Audio verarbeitet")

                # Kopiere in Zwischenablage
                try:
                    pyperclip.copy(full_text)
                    logger.info("📋 Text erfolgreich in Zwischenablage kopiert!")
                except Exception as e:
                    logger.error(f"❌ Fehler beim Kopieren: {e}")
            else:
                logger.warning("⚠️ Kein Text in der Aufnahme erkannt")

        except Exception as e:
            logger.error(f"❌ Fehler bei professioneller Transkription: {e}")
    
    def _clean_transcription_text(self, text: str) -> str:
        """Professionelle Text-Bereinigung."""
        if not text:
            return text
            
        # Entferne "stopp" am Ende
        if text.lower().endswith("stopp"):
            text = text[:-5].strip()
            logger.info("🔧 'stopp' am Ende entfernt")
        
        # Entferne überflüssige Satzzeichen am Ende
        while text and text[-1] in "!?.":
            text = text[:-1].strip()
            logger.info("🔧 Satzzeichen am Ende entfernt")
        
        # Entferne mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_realtime_responses(self) -> List[Dict[str, Any]]:
        """Hole Echtzeit-Antworten."""
        return self.realtime_responses.copy()

def main():
    """Hauptfunktion für professionellen Streaming-Agent."""
    print("🧪 Professioneller Streaming-Agent Test")
    print("=" * 60)
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        default_input_device = sd.query_devices(kind='input')
        print(f"✅ Mikrofon gefunden: {default_input_device['name']}")
    except Exception as e:
        print(f"❌ Mikrofon Fehler: {e}")
        return 1
    
    # Starte professionellen Agent
    print("\n🚀 Starte professionellen Streaming-Agent...")
    agent = ProfessionalStreamingAgent()
    agent.start()
    
    print("\n💡 Professioneller Streaming-Agent läuft!")
    print("🎯 Teste Kato Wake Words:")
    print("   - 'Kato start' / 'Hey Kato start' / 'Okay Kato start'")
    print("   - 'Kato stopp' / 'Kato einfügen' / 'Kato beenden'")
    print("🛑 Kommandos: start, stopp, einfügen, beenden")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            time.sleep(1)
            
            # Zeige Echtzeit-Antworten
            responses = agent.get_realtime_responses()
            if responses:
                latest = responses[-1]
                print(f"🔍 Echtzeit: '{latest['text']}' (Confidence: {latest['confidence']:.2f})")
                
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
    finally:
        agent.stop()
        print("🎉 Test beendet!")

if __name__ == "__main__":
    exit(main())
