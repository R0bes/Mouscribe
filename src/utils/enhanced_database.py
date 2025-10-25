# src/utils/enhanced_database.py - Enhanced Database Manager for Mauscribe
"""
Enhanced database manager supporting dual modes:
- Normal mode: Audio files deleted after transcription
- Enhanced mode: Audio files + transcriptions saved permanently
"""

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RecordingConfig:
    """Configuration for recording behavior."""

    mode: str = "normal"  # 'normal' or 'enhanced'
    session_id: Optional[str] = None
    auto_cleanup: bool = True  # Auto cleanup in normal mode
    cleanup_after_n_recordings: int = 10  # Cleanup after N recordings
    cleanup_on_exit: bool = True  # Cleanup on program exit


class EnhancedAudioDatabase:
    """Enhanced database manager with dual mode support."""

    def __init__(self, db_path: str = "data/audio_database_v2.db"):
        self.db_path = db_path
        self.current_session_id = None
        self.recording_count = 0
        self._ensure_db_directory()
        self._create_tables()

    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Audio recordings table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audio_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    audio_file_path TEXT,
                    duration_seconds REAL NOT NULL,
                    sample_rate INTEGER NOT NULL,
                    channels INTEGER NOT NULL,
                    audio_format TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    audio_data BLOB,
                    mode TEXT NOT NULL DEFAULT 'normal',
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME
                )
            """
            )

            # Transcriptions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audio_recording_id INTEGER NOT NULL,
                    raw_text TEXT NOT NULL,
                    corrected_text TEXT,
                    confidence_score REAL NOT NULL,
                    language TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    model_size TEXT NOT NULL,
                    processing_time_ms INTEGER,
                    word_timestamps TEXT,
                    segments TEXT,
                    is_training_data BOOLEAN DEFAULT FALSE,
                    training_tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (audio_recording_id) REFERENCES audio_recordings (id)
                )
            """
            )

            # Sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    mode TEXT NOT NULL DEFAULT 'normal',
                    total_recordings INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Training data table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription_id INTEGER NOT NULL,
                    audio_recording_id INTEGER NOT NULL,
                    quality_score REAL,
                    speaker_id TEXT,
                    domain TEXT,
                    tags TEXT,
                    is_validated BOOLEAN DEFAULT FALSE,
                    validation_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transcription_id) REFERENCES transcriptions (id),
                    FOREIGN KEY (audio_recording_id) REFERENCES audio_recordings (id)
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_recordings_session ON audio_recordings(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_recordings_mode ON audio_recordings(mode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcriptions_recording ON transcriptions(audio_recording_id)")

            conn.commit()

    def start_session(self, mode: str = "normal", session_id: str = None) -> str:
        """Start a new recording session."""
        if not session_id:
            session_id = f"session_{int(datetime.now().timestamp())}"

        self.current_session_id = session_id

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR IGNORE INTO sessions (id, start_time, mode)
                VALUES (?, ?, ?)
            """,
                (session_id, datetime.now().isoformat(), mode),
            )

            conn.commit()

        return session_id

    def end_session(self):
        """End current session."""
        if not self.current_session_id:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE sessions
                SET end_time = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (self.current_session_id,),
            )

            conn.commit()

        self.current_session_id = None
        self.recording_count = 0

    def save_audio_recording(
        self,
        audio_data: bytes,
        config: RecordingConfig,
        sample_rate: int = 16000,
        channels: int = 1,
        audio_format: str = "wav",
        metadata: dict[str, Any] = None,
    ) -> int:
        """Save audio recording based on mode."""
        if not self.current_session_id:
            self.start_session(config.mode)

        timestamp = datetime.now().isoformat()
        duration = len(audio_data) / (sample_rate * channels * 2)

        # Determine file path and data storage based on mode
        if config.mode == "enhanced":
            # Enhanced mode: save file and store data
            audio_dir = Path("data/audio")
            audio_dir.mkdir(exist_ok=True)
            file_path = audio_dir / f"recording_{int(datetime.now().timestamp())}.wav"

            # Save audio file
            with open(file_path, "wb") as f:
                f.write(audio_data)

            audio_blob = None  # Don't store in DB, use file path
        else:
            # Normal mode: temporary storage, will be cleaned up
            file_path = f"temp_recording_{int(datetime.now().timestamp())}.wav"
            audio_blob = audio_data  # Store temporarily in DB

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO audio_recordings
                (session_id, timestamp, audio_file_path, duration_seconds,
                 sample_rate, channels, audio_format, file_size_bytes,
                 audio_data, mode, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.current_session_id,
                    timestamp,
                    str(file_path),
                    duration,
                    sample_rate,
                    channels,
                    audio_format,
                    len(audio_data),
                    audio_blob,
                    config.mode,
                    json.dumps(metadata) if metadata else None,
                ),
            )

            recording_id = cursor.lastrowid

            # Update session stats
            cursor.execute(
                """
                UPDATE sessions
                SET total_recordings = total_recordings + 1,
                    total_duration = total_duration + ?
                WHERE id = ?
            """,
                (duration, self.current_session_id),
            )

            conn.commit()

        self.recording_count += 1

        # Auto cleanup in normal mode
        if config.mode == "normal" and config.auto_cleanup:
            if self.recording_count >= config.cleanup_after_n_recordings:
                self.cleanup_old_recordings()

        return recording_id

    def save_transcription(
        self,
        audio_recording_id: int,
        raw_text: str,
        confidence: float,
        language: str,
        model_name: str,
        model_size: str,
        processing_time_ms: int = None,
        word_timestamps: list[dict] = None,
        segments: list[dict] = None,
        corrected_text: str = None,
    ) -> int:
        """Save transcription with enhanced metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO transcriptions
                (audio_recording_id, raw_text, corrected_text, confidence_score,
                 language, model_name, model_size, processing_time_ms,
                 word_timestamps, segments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    audio_recording_id,
                    raw_text,
                    corrected_text,
                    confidence,
                    language,
                    model_name,
                    model_size,
                    processing_time_ms,
                    json.dumps(word_timestamps) if word_timestamps else None,
                    json.dumps(segments) if segments else None,
                ),
            )

            transcription_id = cursor.lastrowid
            conn.commit()

        return transcription_id

    def cleanup_old_recordings(self, session_id: str = None):
        """Clean up old recordings in normal mode."""
        target_session = session_id or self.current_session_id

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Mark recordings as deleted
            cursor.execute(
                """
                UPDATE audio_recordings
                SET deleted_at = CURRENT_TIMESTAMP,
                    audio_file_path = NULL,
                    audio_data = NULL
                WHERE session_id = ? AND mode = 'normal' AND deleted_at IS NULL
            """,
                (target_session,),
            )

            conn.commit()

        self.recording_count = 0

    def get_recordings_with_transcriptions(self, mode: str = None, session_id: str = None, limit: int = 50) -> list[dict]:
        """Get recordings with their transcriptions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT
                    a.id, a.session_id, a.timestamp, a.audio_file_path,
                    a.duration_seconds, a.sample_rate, a.channels, a.audio_format,
                    a.file_size_bytes, a.mode, a.metadata,
                    t.id as transcription_id, t.raw_text, t.corrected_text,
                    t.confidence_score, t.language, t.model_name, t.model_size,
                    t.processing_time_ms, t.word_timestamps, t.segments,
                    t.is_training_data, t.training_tags, t.created_at as transcription_created_at
                FROM audio_recordings a
                LEFT JOIN transcriptions t ON a.id = t.audio_recording_id
                WHERE a.deleted_at IS NULL
            """

            params = []
            conditions = []

            if mode:
                conditions.append("a.mode = ?")
                params.append(mode)

            if session_id:
                conditions.append("a.session_id = ?")
                params.append(session_id)

            if conditions:
                query += " AND " + " AND ".join(conditions)

            query += " ORDER BY a.timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def mark_for_training(
        self,
        transcription_id: int,
        quality_score: float = None,
        speaker_id: str = None,
        domain: str = None,
        tags: list[str] = None,
    ):
        """Mark transcription for ML training."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update transcription
            cursor.execute(
                """
                UPDATE transcriptions
                SET is_training_data = TRUE, training_tags = ?
                WHERE id = ?
            """,
                (json.dumps(tags) if tags else None, transcription_id),
            )

            # Get audio recording ID
            cursor.execute("SELECT audio_recording_id FROM transcriptions WHERE id = ?", (transcription_id,))
            result = cursor.fetchone()
            if result:
                audio_recording_id = result[0]

                # Add to training data table
                cursor.execute(
                    """
                    INSERT INTO training_data
                    (transcription_id, audio_recording_id, quality_score, speaker_id, domain, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        transcription_id,
                        audio_recording_id,
                        quality_score,
                        speaker_id,
                        domain,
                        json.dumps(tags) if tags else None,
                    ),
                )

            conn.commit()

    def get_training_data(self, limit: int = 100) -> list[dict]:
        """Get data marked for training."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    td.id, td.quality_score, td.speaker_id, td.domain, td.tags,
                    t.raw_text, t.corrected_text, t.confidence_score, t.language,
                    t.model_name, t.model_size, t.word_timestamps, t.segments,
                    a.audio_file_path, a.duration_seconds, a.sample_rate, a.channels
                FROM training_data td
                JOIN transcriptions t ON td.transcription_id = t.id
                JOIN audio_recordings a ON td.audio_recording_id = a.id
                WHERE a.deleted_at IS NULL
                ORDER BY td.created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def cleanup_on_exit(self):
        """Clean up all normal mode recordings on program exit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE audio_recordings
                SET deleted_at = CURRENT_TIMESTAMP,
                    audio_file_path = NULL,
                    audio_data = NULL
                WHERE mode = 'normal' AND deleted_at IS NULL
            """
            )

            conn.commit()


# Global instance
_enhanced_db = None


def get_enhanced_database() -> EnhancedAudioDatabase:
    """Get global enhanced database instance."""
    global _enhanced_db
    if _enhanced_db is None:
        _enhanced_db = EnhancedAudioDatabase()
    return _enhanced_db
