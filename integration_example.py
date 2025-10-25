# Integration example for MauscribeApp
"""
Example of how to integrate the new enhanced database into MauscribeApp.
This shows the key changes needed in the main application.
"""

# In src/mouscribe.py - Key changes needed:


class MauscribeApp:
    def __init__(self):
        # ... existing initialization ...

        # New: Enhanced database and recording config
        from .config.recording_modes import DEFAULT_ENHANCED_CONFIG, DEFAULT_NORMAL_CONFIG, RecordingMode
        from .utils.enhanced_database import RecordingConfig, get_enhanced_database

        self.enhanced_db = get_enhanced_database()
        self.recording_config = DEFAULT_NORMAL_CONFIG  # Default to normal mode

        # Check if enhanced mode is enabled in settings
        if hasattr(self.config, "enhanced_mode") and self.config.enhanced_mode:
            self.recording_config = DEFAULT_ENHANCED_CONFIG
            self.logger.info("🎯 Enhanced mode enabled - Audio files will be saved permanently")
        else:
            self.logger.info("📝 Normal mode enabled - Audio files will be cleaned up after transcription")

    def start_recording(self) -> None:
        """Start recording with enhanced database support."""
        try:
            # Start session if not already started
            if not self.enhanced_db.current_session_id:
                session_id = self.enhanced_db.start_session(mode=self.recording_config.mode.value)
                self.logger.info(f"🎙️ Started recording session: {session_id}")

            # Start recording (existing code)
            self.recorder.start_recording()
            self._is_recording = True

            # Emit event (existing code)
            emit_event(
                EventType.RECORDING_STARTED,
                {
                    "timestamp": time.time(),
                    "recorder_state": self.recorder.is_recording,
                    "mode": self.recording_config.mode.value,
                },
                source="MauscribeApp",
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to start recording: {e}")
            raise

    def stop_recording(self) -> None:
        """Stop recording and save to enhanced database."""
        try:
            # Stop recording (existing code)
            self.recorder.stop_recording()
            audio_data = self.recorder.get_audio_data()
            self._is_recording = False

            # Save to enhanced database
            recording_id = self.enhanced_db.save_audio_recording(
                audio_data=audio_data,
                config=self.recording_config,
                sample_rate=self.recorder.sample_rate_hz,
                channels=self.recorder.num_channels,
                audio_format=self.config.database.audio_format,
                metadata={
                    "recorder_settings": {
                        "sample_rate": self.recorder.sample_rate_hz,
                        "channels": self.recorder.num_channels,
                        "format": self.config.database.audio_format,
                    },
                    "app_version": "2.0",
                    "mode": self.recording_config.mode.value,
                },
            )

            self.logger.info(f"💾 Audio recording saved (ID: {recording_id}, Mode: {self.recording_config.mode.value})")

            # Emit event (existing code)
            emit_event(
                EventType.RECORDING_STOPPED,
                {
                    "timestamp": time.time(),
                    "recorder_state": self.recorder.is_recording,
                    "recording_id": recording_id,
                    "mode": self.recording_config.mode.value,
                },
                source="MauscribeApp",
            )

            # Start transcription (existing code)
            self._transcribe_in_background(audio_data, recording_id)

        except Exception as e:
            self.logger.error(f"❌ Failed to stop recording: {e}")
            raise

    def _transcribe_in_background(self, audio_data: bytes, recording_id: int) -> None:
        """Transcribe audio with enhanced database support."""

        def transcribe_thread():
            try:
                # Emit transcription started event
                emit_event(
                    EventType.TRANSCRIPTION_STARTED,
                    {"timestamp": time.time(), "audio_length": len(audio_data), "recording_id": recording_id},
                    source="MauscribeApp",
                )

                # Transcribe (existing code)
                result = self.audio_service.transcribe(audio_data, model_size=self.config.model, language=self.config.language)

                if result:
                    raw_text = result.text
                    confidence = result.confidence

                    # Save transcription to enhanced database
                    transcription_id = self.enhanced_db.save_transcription(
                        audio_recording_id=recording_id,
                        raw_text=raw_text,
                        confidence=confidence,
                        language=result.language,
                        model_name="whisper",
                        model_size=self.config.model,
                        processing_time_ms=int(result.processing_time * 1000) if hasattr(result, "processing_time") else None,
                        word_timestamps=getattr(result, "word_timestamps", None),
                        segments=getattr(result, "segments", None),
                        corrected_text=None,  # Can be filled later
                    )

                    # Auto-mark for training if conditions are met
                    if self.recording_config.training_config.auto_mark_high_confidence:
                        if confidence >= self.recording_config.training_config.min_confidence_threshold:
                            self.enhanced_db.mark_for_training(
                                transcription_id=transcription_id,
                                quality_score=confidence,
                                domain="general",  # Can be made configurable
                            )
                            self.logger.info(
                                f"🎯 Transcription {transcription_id} marked for training (confidence: {confidence:.2%})"
                            )

                    # Emit transcription completed event
                    emit_event(
                        EventType.TRANSCRIPTION_COMPLETED,
                        {
                            "timestamp": time.time(),
                            "text": raw_text,
                            "confidence": confidence,
                            "model": result.model,
                            "language": result.language,
                            "recording_id": recording_id,
                            "transcription_id": transcription_id,
                        },
                        source="MauscribeApp",
                    )

                    # Display transcription (existing code)
                    self._schedule_transcription_display(raw_text, confidence, 0, 0, len(audio_data))

                else:
                    self.logger.warning("⚠️ No transcription result")
                    emit_event(
                        EventType.TRANSCRIPTION_FAILED,
                        {"timestamp": time.time(), "recording_id": recording_id, "error": "No transcription result"},
                        source="MauscribeApp",
                    )

            except Exception as e:
                self.logger.error(f"❌ Transcription error: {e}")
                emit_event(
                    EventType.TRANSCRIPTION_FAILED,
                    {"timestamp": time.time(), "recording_id": recording_id, "error": str(e)},
                    source="MauscribeApp",
                )

        # Start transcription thread
        threading.Thread(target=transcribe_thread, daemon=True).start()

    def switch_recording_mode(self, mode: str) -> None:
        """Switch between normal and enhanced recording modes."""
        from .config.recording_modes import DEFAULT_ENHANCED_CONFIG, DEFAULT_NORMAL_CONFIG, RecordingMode

        if mode == "normal":
            self.recording_config = DEFAULT_NORMAL_CONFIG
            self.logger.info("📝 Switched to Normal mode - Audio files will be cleaned up")
        elif mode == "enhanced":
            self.recording_config = DEFAULT_ENHANCED_CONFIG
            self.logger.info("🎯 Switched to Enhanced mode - Audio files will be saved permanently")
        else:
            raise ValueError(f"Invalid recording mode: {mode}")

        # End current session and start new one
        if self.enhanced_db.current_session_id:
            self.enhanced_db.end_session()
            self.enhanced_db.start_session(mode=mode)

    def cleanup_on_exit(self) -> None:
        """Clean up resources on exit."""
        try:
            # End current session
            if self.enhanced_db.current_session_id:
                self.enhanced_db.end_session()

            # Cleanup normal mode recordings if configured
            if self.recording_config.normal_config.cleanup_on_exit:
                self.enhanced_db.cleanup_on_exit()
                self.logger.info("🧹 Cleaned up normal mode recordings on exit")

            self.logger.info("✅ Enhanced database cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")

    def get_recording_stats(self) -> dict:
        """Get recording statistics."""
        try:
            recordings = self.enhanced_db.get_recordings_with_transcriptions(session_id=self.enhanced_db.current_session_id)

            stats = {
                "current_session": self.enhanced_db.current_session_id,
                "mode": self.recording_config.mode.value,
                "total_recordings": len(recordings),
                "recordings_with_transcriptions": len([r for r in recordings if r.get("transcription_id")]),
                "total_duration": sum(r.get("duration_seconds", 0) for r in recordings),
                "average_confidence": 0.0,
            }

            transcriptions = [r for r in recordings if r.get("confidence_score")]
            if transcriptions:
                stats["average_confidence"] = sum(r["confidence_score"] for r in transcriptions) / len(transcriptions)

            return stats

        except Exception as e:
            self.logger.error(f"❌ Error getting recording stats: {e}")
            return {}


# Example usage in main():
"""
if __name__ == "__main__":
    app = MauscribeApp()

    try:
        app.run()
    finally:
        app.cleanup_on_exit()
"""
