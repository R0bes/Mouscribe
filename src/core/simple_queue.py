# src/core/simple_queue.py
"""
Simple transcription queue for non-blocking audio processing
"""
import queue
import threading
import time
from typing import Any, Callable, Dict

import numpy as np

from ..utils.logger import get_logger


class SimpleTranscriptionQueue:
    """Einfache Queue für sofortige ruckelfreie Lösung"""

    def __init__(self, stt_engine):
        self.stt_engine = stt_engine
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.running = True
        self.callback = None
        self.logger = get_logger(self.__class__.__name__)

    def start(self, callback: Callable):
        """Starte Worker-Thread"""
        self.callback = callback
        self.worker_thread = threading.Thread(
            target=self._worker_loop, name="TranscriptionWorker", daemon=True
        )
        self.worker_thread.start()

    def submit_task(self, audio_data: np.ndarray):
        """Submit task (NON-BLOCKING)"""
        task = {
            "audio_data": audio_data,
            "timestamp": time.time(),
            "task_id": f"task_{int(time.time() * 1000)}",
        }
        self.task_queue.put(task)
        self.logger.debug(f"📋 Task zur Queue hinzugefügt: {task['task_id']}")

    def _worker_loop(self):
        """Verarbeitet Tasks aus der Queue"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1.0)

                # Transkription ausführen
                start_time = time.time()
                result = self.stt_engine.transcribe_raw(task["audio_data"])
                processing_time = time.time() - start_time

                # Callback mit erweiterten Daten
                if self.callback:
                    callback_data = {
                        "text": result,
                        "task_id": task["task_id"],
                        "timestamp": task["timestamp"],
                        "audio_data": task["audio_data"],  # Für späteres Fine-Tuning
                        "processing_time": processing_time,
                    }
                    self.callback(callback_data)

            except queue.Empty:
                continue  # Keine Tasks verfügbar
            except Exception as e:
                self.logger.error(f"❌ Fehler in Transkription: {e}")

    def stop(self):
        """Stoppe Worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

    def get_queue_size(self) -> int:
        """Gib aktuelle Queue-Größe zurück"""
        return self.task_queue.qsize()

    def is_processing(self) -> bool:
        """Prüfe ob gerade verarbeitet wird"""
        return not self.task_queue.empty()

    def update_stt_engine(self, new_stt_engine):
        """Update STT engine with new instance.

        Args:
            new_stt_engine: New STT engine instance
        """
        self.stt_engine = new_stt_engine
        self.logger.info("🔄 STT engine updated in transcription queue")
