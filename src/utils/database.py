"""
Database module for Mauscribe audio recordings and transcriptions.
Provides storage and retrieval of audio data for training purposes.
"""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Literal

import numpy as np
from pydantic import Field

from .settings import Settings
from .logger import get_logger


class DatabaseSettings(Settings):
    """Database settings."""
    enabled: bool = Field(default=True, description="Enable database")
    data_directory: str = Field(default="", description="Data directory path")
    audio_format: Literal["wav", "mp3", "flac"] = Field(default="wav", description="Audio format for storage")
    auto_save_recordings: bool = Field(default=True, description="Auto-save recordings")
    auto_save_transcriptions: bool = Field(default=True, description="Auto-save transcriptions")
    mark_as_training_data: bool = Field(default=True, description="Mark data as training data")
    retention_days: int = Field(default=30, ge=1, le=365, description="Data retention in days")
    max_size_mb: int = Field(default=1000, ge=100, le=10000, description="Maximum database size in MB")
    compress_audio: bool = Field(default=False, description="Compress audio files")
    backup_before_cleanup: bool = Field(default=True, description="Backup before cleanup")
    model_config = { "env_prefix": "MAUSCRIBE_DB_" }
    
class AudioDatabase:
    """Database manager for audio recordings and transcriptions."""

    def __init__(self) -> None:
        """Initialize the audio database."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = DatabaseSettings()

        # Database path
        if self.config.data_directory:
            data_dir = Path(self.config.data_directory)
        else:
            # Use absolute path from current working directory
            data_dir = Path.cwd() / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "audio_database.db"

        self.db_path = str(db_path)
        self.logger.info(f"🗄️  Initialisiere Audio-Datenbank: {self.db_path}")

        # Store data_dir for later use
        self.data_dir = data_dir

        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create audio_recordings table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audio_recordings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        audio_file_path TEXT NOT NULL,
                        duration_seconds REAL,
                        sample_rate INTEGER,
                        channels INTEGER,
                        audio_format TEXT,
                        file_size_bytes INTEGER,
                        metadata TEXT
                    )
                """
                )

                # Create transcriptions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transcriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        audio_recording_id INTEGER,
                        raw_text TEXT NOT NULL,
                        corrected_text TEXT,
                        confidence_score REAL,
                        language TEXT,
                        processing_time_ms INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (audio_recording_id) REFERENCES audio_recordings(id)
                    )
                """
                )

                # Create training_data table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS training_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transcription_id INTEGER,
                        is_valid_for_training BOOLEAN DEFAULT TRUE,
                        quality_score REAL,
                        notes TEXT,
                        tags TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (transcription_id) REFERENCES transcriptions(id)
                    )
                """
                )

                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audio_timestamp ON audio_recordings(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcription_audio_id ON transcriptions(audio_recording_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_transcription_id ON training_data(transcription_id)")

                conn.commit()
                self.logger.info("✅ Datenbank-Tabellen erfolgreich initialisiert")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def save_audio_recording(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        channels: int,
        duration: float,
        audio_format: str = "mp3",
    ) -> int:
        """Save audio recording to file and database with compression."""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"recording_{timestamp}.{audio_format}"

            # Ensure audio directory exists
            if self.config.database_data_directory:
                audio_dir = Path(self.config.database_data_directory) / "audio"
            else:
                # Use absolute path from current working directory
                audio_dir = Path.cwd() / "data" / "audio"

            # Create directory structure
            audio_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Audio directory ensured: {audio_dir}")

            audio_file_path = audio_dir / filename

            # Save audio file with compression
            actual_file_path = self._save_audio_file(audio_data, audio_file_path, sample_rate, channels, audio_format)

            # Get file size from actual saved file
            if actual_file_path and actual_file_path.exists():
                file_size = actual_file_path.stat().st_size
                final_file_path = str(actual_file_path)
            else:
                # Fallback: use original path
                file_size = audio_file_path.stat().st_size if audio_file_path.exists() else 0
                final_file_path = str(audio_file_path)

            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO audio_recordings
                    (audio_file_path, duration_seconds, sample_rate, channels, audio_format, file_size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        final_file_path,
                        duration,
                        sample_rate,
                        channels,
                        audio_format,
                        file_size,
                    ),
                )

                recording_id = cursor.lastrowid
                conn.commit()

                if recording_id is None:
                    raise RuntimeError("Failed to get recording ID from database")

                self.logger.info(f"✅ Audio recording saved with ID: {recording_id} to {final_file_path}")
                return recording_id

        except Exception as e:
            self.logger.error(f"❌ Failed to save audio recording: {e}")
            raise

    def _save_audio_file(
        self,
        audio_data: np.ndarray,
        file_path: Path,
        sample_rate: int,
        channels: int,
        format: str,
    ) -> Path:
        """Save audio data to file with compression."""
        try:
            # Try to use soundfile for WAV first
            if format.lower() == "wav":
                try:
                    import soundfile as sf

                    sf.write(str(file_path), audio_data, sample_rate)
                    self.logger.debug(f"✅ Audio saved as WAV: {file_path}")
                    return file_path
                except ImportError:
                    self.logger.warning("soundfile not available for WAV, trying pydub...")
                except Exception as e:
                    self.logger.warning(f"soundfile failed for WAV: {e}, trying pydub...")

            # Try to use pydub for MP3/OGG compression
            try:
                from pydub import AudioSegment

                # Convert numpy array to AudioSegment
                # Normalize audio to 16-bit range
                audio_normalized = np.int16(audio_data * 32767)

                # Create AudioSegment from numpy array
                audio_segment = AudioSegment(
                    audio_normalized.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=1 if audio_data.ndim == 1 else audio_data.shape[1],
                )

                # Save with compression
                if format.lower() == "mp3":
                    audio_segment.export(str(file_path), format="mp3", bitrate="128k")
                elif format.lower() == "ogg":
                    audio_segment.export(str(file_path), format="ogg", bitrate="128k")
                else:
                    # Fallback to WAV
                    audio_segment.export(str(file_path), format="wav")

                self.logger.debug(f"✅ Audio saved as {format.upper()}: {file_path}")
                return file_path

            except ImportError:
                self.logger.warning("pydub not available, trying soundfile...")
            except Exception as e:
                self.logger.warning(f"pydub failed: {e}, trying soundfile...")

            # Try soundfile as fallback
            try:
                import soundfile as sf

                sf.write(str(file_path), audio_data, sample_rate)
                self.logger.debug(f"✅ Audio saved with soundfile: {file_path}")
                return file_path
            except ImportError:
                self.logger.warning("soundfile not available, using numpy.save as fallback")
            except Exception as e:
                self.logger.warning(f"soundfile failed: {e}, using numpy.save as fallback")

            # Final fallback: numpy.save
            self.logger.warning("Using numpy.save as fallback - no compression")
            npy_file_path = file_path.with_suffix(".npy")
            np.save(str(npy_file_path), audio_data)

            # WICHTIG: Aktualisiere den file_path Parameter, damit die aufrufende Methode den korrekten Pfad kennt
            # Da wir den Parameter nicht direkt ändern können, müssen wir das in der aufrufenden Methode behandeln
            return npy_file_path

        except Exception as e:
            self.logger.error(f"❌ Failed to save audio file: {e}")
            # Last resort: numpy.save
            try:
                npy_file_path = file_path.with_suffix(".npy")
                np.save(str(npy_file_path), audio_data)
                self.logger.info(f"✅ Audio saved as numpy array: {npy_file_path}")
                return npy_file_path
            except Exception as e2:
                self.logger.error(f"❌ Even numpy.save failed: {e2}")
                raise e

    def save_transcription(
        self,
        audio_recording_id: int,
        raw_text: str,
        corrected_text: Optional[str] = None,
        confidence_score: Optional[float] = None,
        language: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
    ) -> int:
        """Save transcription to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO transcriptions
                    (audio_recording_id, raw_text, corrected_text, confidence_score, language, processing_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        audio_recording_id,
                        raw_text,
                        corrected_text,
                        confidence_score,
                        language,
                        processing_time_ms,
                    ),
                )

                transcription_id = cursor.lastrowid
                conn.commit()

                if transcription_id is None:
                    raise RuntimeError("Failed to get transcription ID from database")

                self.logger.info(f"Transcription saved with ID: {transcription_id}")
                return transcription_id

        except Exception as e:
            self.logger.error(f"Failed to save transcription: {e}")
            raise

    def save_training_data(
        self,
        transcription_id: int,
        is_valid_for_training: bool = True,
        quality_score: Optional[float] = None,
        notes: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> int:
        """Save training data metadata."""
        try:
            tags_json = json.dumps(tags) if tags else None

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO training_data
                    (transcription_id, is_valid_for_training, quality_score, notes, tags)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        transcription_id,
                        is_valid_for_training,
                        quality_score,
                        notes,
                        tags_json,
                    ),
                )

                training_data_id = cursor.lastrowid
                conn.commit()

                if training_data_id is None:
                    raise RuntimeError("Failed to get training data ID from database")

                self.logger.info(f"Training data saved with ID: {training_data_id}")
                return training_data_id

        except Exception as e:
            self.logger.error(f"Failed to save training data: {e}")
            raise

    def get_recordings_for_training(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """Get recordings marked as valid for training."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query = """
                    SELECT
                        ar.id as recording_id,
                        ar.audio_file_path,
                        ar.duration_seconds,
                        ar.sample_rate,
                        ar.channels,
                        ar.timestamp,
                        t.id as transcription_id,
                        t.raw_text,
                        t.corrected_text,
                        t.language,
                        td.quality_score,
                        td.notes,
                        td.tags
                    FROM audio_recordings ar
                    JOIN transcriptions t ON ar.id = t.audio_recording_id
                    JOIN training_data td ON t.id = td.transcription_id
                    WHERE td.is_valid_for_training = TRUE
                    ORDER BY ar.timestamp DESC
                """

                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                # Convert to list of dictionaries
                result = []
                for row in rows:
                    row_dict = dict(row)
                    if row_dict["tags"]:
                        row_dict["tags"] = json.loads(row_dict["tags"])
                    result.append(row_dict)

                return result

        except Exception as e:
            self.logger.error(f"Failed to get training data: {e}")
            return []

    def get_statistics(self) -> dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total recordings
                cursor.execute("SELECT COUNT(*) FROM audio_recordings")
                total_recordings = cursor.fetchone()[0]

                # Total transcriptions
                cursor.execute("SELECT COUNT(*) FROM transcriptions")
                total_transcriptions = cursor.fetchone()[0]

                # Training data count
                cursor.execute("SELECT COUNT(*) FROM training_data WHERE is_valid_for_training = TRUE")
                training_count = cursor.fetchone()[0]

                # Total duration
                cursor.execute("SELECT SUM(duration_seconds) FROM audio_recordings")
                total_duration = cursor.fetchone()[0] or 0

                # Total file size
                cursor.execute("SELECT SUM(file_size_bytes) FROM audio_recordings")
                total_size = cursor.fetchone()[0] or 0

                return {
                    "total_recordings": total_recordings,
                    "total_transcriptions": total_transcriptions,
                    "training_samples": training_count,
                    "total_duration_hours": total_duration / 3600,
                    "total_size_mb": total_size / (1024 * 1024),
                }

        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}

    def export_training_data(self, output_file: str) -> bool:
        """Export training data to JSON file for external use."""
        try:
            training_data = self.get_recordings_for_training()

            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_samples": len(training_data),
                "samples": training_data,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Training data exported to: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export training data: {e}")
            return False

    def cleanup_old_recordings(self, days_to_keep: int = 30) -> int:
        """Remove old recordings and files."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get old recordings
                cursor.execute(
                    """
                    SELECT audio_file_path FROM audio_recordings
                    WHERE timestamp < datetime(?, 'unixepoch')
                """,
                    (cutoff_date,),
                )

                old_files = cursor.fetchall()
                deleted_count = 0

                for (file_path,) in old_files:
                    try:
                        # Delete file
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to delete file {file_path}: {e}")

                # Delete database records
                cursor.execute(
                    """
                    DELETE FROM audio_recordings
                    WHERE timestamp < datetime(?, 'unixepoch')
                """,
                    (cutoff_date,),
                )

                conn.commit()

                self.logger.info(f"Cleaned up {deleted_count} old recordings")
                return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old recordings: {e}")
            return 0
