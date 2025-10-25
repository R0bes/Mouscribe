import os
import sqlite3
from datetime import datetime
from pathlib import Path


class NewAudioDatabase:
    """New database structure for Mauscribe with dual modes."""

    def __init__(self, db_path: str = "data/audio_database_v2.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_tables()

    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _create_tables(self):
        """Create new database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Audio recordings table - enhanced structure
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audio_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,  -- Groups recordings from same session
                    timestamp DATETIME NOT NULL,
                    audio_file_path TEXT,  -- NULL in normal mode (file deleted)
                    duration_seconds REAL NOT NULL,
                    sample_rate INTEGER NOT NULL,
                    channels INTEGER NOT NULL,
                    audio_format TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    audio_data BLOB,  -- Store audio data directly in DB for enhanced mode
                    mode TEXT NOT NULL DEFAULT 'normal',  -- 'normal' or 'enhanced'
                    metadata TEXT,  -- JSON string for additional data
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME  -- When audio file was deleted (normal mode)
                )
            """
            )

            # Transcriptions table - enhanced structure
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audio_recording_id INTEGER NOT NULL,
                    raw_text TEXT NOT NULL,
                    corrected_text TEXT,
                    confidence_score REAL NOT NULL,
                    language TEXT NOT NULL,
                    model_name TEXT NOT NULL,  -- Which Whisper model was used
                    model_size TEXT NOT NULL,  -- tiny, base, small, medium, large
                    processing_time_ms INTEGER,
                    word_timestamps TEXT,  -- JSON array of word-level timestamps
                    segments TEXT,  -- JSON array of segment-level data
                    is_training_data BOOLEAN DEFAULT FALSE,  -- Mark for ML training
                    training_tags TEXT,  -- Tags for training data organization
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (audio_recording_id) REFERENCES audio_recordings (id)
                )
            """
            )

            # Sessions table - for grouping recordings
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

            # Training data table - for ML training organization
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription_id INTEGER NOT NULL,
                    audio_recording_id INTEGER NOT NULL,
                    quality_score REAL,  -- Manual quality rating
                    speaker_id TEXT,  -- For multi-speaker training
                    domain TEXT,  -- e.g., 'general', 'technical', 'casual'
                    tags TEXT,  -- JSON array of tags
                    is_validated BOOLEAN DEFAULT FALSE,
                    validation_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transcription_id) REFERENCES transcriptions (id),
                    FOREIGN KEY (audio_recording_id) REFERENCES audio_recordings (id)
                )
            """
            )

            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_recordings_session ON audio_recordings(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_recordings_mode ON audio_recordings(mode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcriptions_recording ON transcriptions(audio_recording_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcriptions_model ON transcriptions(model_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_data_transcription ON training_data(transcription_id)")

            conn.commit()

    def save_recording(
        self,
        audio_data: bytes,
        session_id: str,
        mode: str = "normal",
        sample_rate: int = 16000,
        channels: int = 1,
        audio_format: str = "wav",
        metadata: dict = None,
    ) -> int:
        """Save audio recording with enhanced structure."""
        import time

        timestamp = datetime.now().isoformat()
        duration = len(audio_data) / (sample_rate * channels * 2)  # Rough duration calculation

        # In normal mode, don't store audio data
        audio_blob = audio_data if mode == "enhanced" else None
        file_path = None if mode == "normal" else f"data/audio/recording_{int(time.time())}.wav"

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
                    session_id,
                    timestamp,
                    file_path,
                    duration,
                    sample_rate,
                    channels,
                    audio_format,
                    len(audio_data),
                    audio_blob,
                    mode,
                    str(metadata) if metadata else None,
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
                (duration, session_id),
            )

            conn.commit()

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
        word_timestamps: list = None,
        segments: list = None,
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
                    str(word_timestamps) if word_timestamps else None,
                    str(segments) if segments else None,
                ),
            )

            transcription_id = cursor.lastrowid
            conn.commit()

        return transcription_id

    def create_session(self, session_id: str = None, mode: str = "normal") -> str:
        """Create a new recording session."""
        if not session_id:
            session_id = f"session_{int(datetime.now().timestamp())}"

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

    def cleanup_normal_mode(self, session_id: str = None):
        """Clean up audio files in normal mode after transcription."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if session_id:
                # Clean up specific session
                cursor.execute(
                    """
                    UPDATE audio_recordings
                    SET deleted_at = CURRENT_TIMESTAMP,
                        audio_file_path = NULL,
                        audio_data = NULL
                    WHERE session_id = ? AND mode = 'normal' AND deleted_at IS NULL
                """,
                    (session_id,),
                )
            else:
                # Clean up all normal mode recordings
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

    def get_recordings_with_transcriptions(self, mode: str = None, limit: int = 50):
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
            if mode:
                query += " AND a.mode = ?"
                params.append(mode)

            query += " ORDER BY a.timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def mark_for_training(
        self, transcription_id: int, quality_score: float = None, speaker_id: str = None, domain: str = None, tags: list = None
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
                (str(tags) if tags else None, transcription_id),
            )

            # Get audio recording ID
            cursor.execute("SELECT audio_recording_id FROM transcriptions WHERE id = ?", (transcription_id,))
            audio_recording_id = cursor.fetchone()[0]

            # Add to training data table
            cursor.execute(
                """
                INSERT INTO training_data
                (transcription_id, audio_recording_id, quality_score, speaker_id, domain, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (transcription_id, audio_recording_id, quality_score, speaker_id, domain, str(tags) if tags else None),
            )

            conn.commit()


# Test the new database
if __name__ == "__main__":
    print("=== CREATING NEW DATABASE STRUCTURE ===")

    # Create new database
    db = NewAudioDatabase()
    print(f"New database created: {db.db_path}")

    # Create a test session
    session_id = db.create_session(mode="enhanced")
    print(f"Test session created: {session_id}")

    # Test saving a recording (with dummy data)
    test_audio_data = b"dummy audio data for testing"
    recording_id = db.save_recording(
        audio_data=test_audio_data,
        session_id=session_id,
        mode="enhanced",
        sample_rate=16000,
        channels=1,
        audio_format="wav",
        metadata={"test": True},
    )
    print(f"Test recording saved: {recording_id}")

    # Test saving a transcription
    transcription_id = db.save_transcription(
        audio_recording_id=recording_id,
        raw_text="This is a test transcription",
        confidence=0.95,
        language="en",
        model_name="whisper",
        model_size="base",
        processing_time_ms=1500,
    )
    print(f"Test transcription saved: {transcription_id}")

    # Test retrieving data
    recordings = db.get_recordings_with_transcriptions(mode="enhanced", limit=10)
    print(f"Retrieved {len(recordings)} recordings with transcriptions")

    print("\n=== NEW DATABASE STRUCTURE READY ===")
    print("Features:")
    print("- Dual mode support (normal/enhanced)")
    print("- Session-based organization")
    print("- Enhanced transcription metadata")
    print("- Training data management")
    print("- Automatic cleanup in normal mode")
