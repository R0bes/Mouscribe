# src/utils/eventbus.py - Event Bus System
"""
Event Bus for real-time communication between Mauscribe components.
Enables live updates in Control Center without polling.
"""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class EventType(Enum):
    """Event types for Mauscribe application."""

    # Recording events
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    RECORDING_DURATION_UPDATE = "recording_duration_update"

    # Transcription events
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_COMPLETED = "transcription_completed"
    TRANSCRIPTION_FAILED = "transcription_failed"

    # Audio file events
    AUDIO_FILE_SAVED = "audio_file_saved"
    AUDIO_FILE_DELETED = "audio_file_deleted"

    # System events
    SYSTEM_STATUS_CHANGED = "system_status_changed"
    LOG_MESSAGE_ADDED = "log_message_added"


@dataclass
class Event:
    """Event data structure."""

    event_type: EventType
    data: dict[str, Any]
    timestamp: float
    source: str


class EventBus:
    """Event Bus for real-time communication."""

    def __init__(self):
        """Initialize the Event Bus."""
        self._subscribers: dict[EventType, list[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()
        self._event_history: list[Event] = []
        self._max_history = 1000

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass  # Callback not found

    def emit(self, event_type: EventType, data: dict[str, Any], source: str = "unknown") -> None:
        """Emit an event to all subscribers.

        Args:
            event_type: Type of event to emit
            data: Event data
            source: Source component name
        """
        event = Event(event_type=event_type, data=data, timestamp=time.time(), source=source)

        # Add to history
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

        # Notify subscribers
        with self._lock:
            subscribers = self._subscribers.get(event_type, []).copy()

        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")

    def get_recent_events(self, event_type: Optional[EventType] = None, limit: int = 50) -> list[Event]:
        """Get recent events.

        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        with self._lock:
            events = self._event_history.copy()

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:] if events else []

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance.

    Returns:
        Global EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def emit_event(event_type: EventType, data: dict[str, Any], source: str = "unknown") -> None:
    """Emit an event using the global event bus.

    Args:
        event_type: Type of event to emit
        data: Event data
        source: Source component name
    """
    get_event_bus().emit(event_type, data, source)


def subscribe_to_event(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """Subscribe to an event using the global event bus.

    Args:
        event_type: Type of event to subscribe to
        callback: Function to call when event occurs
    """
    get_event_bus().subscribe(event_type, callback)


def unsubscribe_from_event(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """Unsubscribe from an event using the global event bus.

    Args:
        event_type: Type of event to unsubscribe from
        callback: Function to remove from subscribers
    """
    get_event_bus().unsubscribe(event_type, callback)
