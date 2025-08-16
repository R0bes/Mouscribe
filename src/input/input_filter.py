# src/input/input_filter.py - Input filtering for Mauscribe
"""
Input filtering system for Mauscribe application.
Provides different input modes: single click, double click, hold, and smart detection.
"""

import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from ..utils.logger import get_logger


class InputMode(Enum):
    """Available input filter modes."""

    SINGLE_CLICK = "single_click"
    DOUBLE_CLICK = "double_click"
    HOLD = "hold"
    SMART = "smart"


class InputFilter:
    """Input filter that processes raw input events based on configured mode."""

    def __init__(self, config) -> None:
        """Initialize the input filter.

        Args:
            config: Configuration object with input filter settings
        """
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

        # Input state tracking
        self.primary_button_state = False
        self.secondary_button_state = False
        self.primary_press_time = 0.0
        self.secondary_press_time = 0.0
        self.primary_click_count = 0
        self.secondary_click_count = 0
        self.last_primary_click_time = 0.0
        self.last_secondary_click_time = 0.0

        # Hold detection
        self.primary_hold_timer: Optional[threading.Timer] = None
        self.secondary_hold_timer: Optional[threading.Timer] = None

        # Smart mode state
        self.primary_smart_timer: Optional[threading.Timer] = None
        self.secondary_smart_timer: Optional[threading.Timer] = None

        # Callbacks
        self.primary_callback: Optional[Callable[[bool], None]] = None
        self.secondary_callback: Optional[Callable[[bool], None]] = None

        # Get current modes
        self._update_modes()

    def set_callbacks(
        self,
        primary_callback: Callable[[bool], None],
        secondary_callback: Callable[[bool], None],
    ) -> None:
        """Set the callback functions for filtered input events.

        Args:
            primary_callback: Callback for primary button events
            secondary_callback: Callback for secondary button events
        """
        self.primary_callback = primary_callback
        self.secondary_callback = secondary_callback

    def _update_modes(self) -> None:
        """Update the current input filter modes from configuration."""
        try:
            # Versuche zuerst die neuen primary/secondary Konfigurationen zu verwenden
            primary_method = self.config.primary_method
            if "press" in primary_method or "klick" in primary_method:
                self.primary_mode = InputMode.SINGLE_CLICK
            elif "hold" in primary_method:
                self.primary_mode = InputMode.HOLD
            elif "double_click" in primary_method:
                self.primary_mode = InputMode.DOUBLE_CLICK
            else:
                # Fallback auf die alte input_filter Konfiguration
                primary_mode_str = self.config.input_filter_primary_mode
                self.primary_mode = InputMode(primary_mode_str)
            
            self.logger.info(
                f"Primary button filter mode set to: {self.primary_mode.value}"
            )
        except (ValueError, AttributeError):
            self.logger.warning(
                f"Invalid primary button filter mode, using single_click"
            )
            self.primary_mode = InputMode.SINGLE_CLICK

        try:
            # Versuche zuerst die neuen primary/secondary Konfigurationen zu verwenden
            secondary_method = self.config.secondary_method
            if "press" in secondary_method or "klick" in secondary_method:
                self.secondary_mode = InputMode.SINGLE_CLICK
            elif "hold" in secondary_method:
                self.secondary_mode = InputMode.HOLD
            elif "double_click" in secondary_method:
                self.secondary_mode = InputMode.DOUBLE_CLICK
            else:
                # Fallback auf die alte input_filter Konfiguration
                secondary_mode_str = self.config.input_filter_secondary_mode
                self.secondary_mode = InputMode(secondary_mode_str)
            
            self.logger.info(
                f"Secondary button filter mode set to: {self.secondary_mode.value}"
            )
        except (ValueError, AttributeError):
            self.logger.warning(
                f"Invalid secondary button filter mode, using hold"
            )
            self.secondary_mode = InputMode.HOLD

    def process_primary_input(self, pressed: bool) -> None:
        """Process primary button input based on current filter mode.

        Args:
            pressed: True if button is pressed, False if released
        """
        current_time = time.time()

        if pressed:
            self._handle_primary_press(current_time)
        else:
            self._handle_primary_release(current_time)

    def process_secondary_input(self, pressed: bool) -> None:
        """Process secondary button input based on current filter mode.

        Args:
            pressed: True if button is pressed, False if released
        """
        current_time = time.time()

        if pressed:
            self._handle_secondary_press(current_time)
        else:
            self._handle_secondary_release(current_time)

    def _handle_primary_press(self, current_time: float) -> None:
        """Handle primary button press event."""
        self.primary_button_state = True
        self.primary_press_time = current_time

        # Versuche zuerst die neue primary Konfiguration zu verwenden
        try:
            primary_method = self.config.primary_method
            if "press" in primary_method or "klick" in primary_method:
                # Direkte Auslösung bei Press/Klick
                self._trigger_primary_callback(True)
                return
        except (AttributeError, KeyError, TypeError):
            pass

        # Fallback auf die alten Modi
        if self.primary_mode == InputMode.SINGLE_CLICK:
            self._trigger_primary_callback(True)
        elif self.primary_mode == InputMode.DOUBLE_CLICK:
            self._handle_double_click_primary(current_time)
        elif self.primary_mode == InputMode.HOLD:
            self._start_primary_hold_timer()
        elif self.primary_mode == InputMode.SMART:
            self._start_primary_smart_timer()

    def _handle_primary_release(self, current_time: float) -> None:
        """Handle primary button release event."""
        self.primary_button_state = False

        if self.primary_mode == InputMode.HOLD:
            self._cancel_primary_hold_timer()
        elif self.primary_mode == InputMode.SMART:
            self._cancel_primary_smart_timer()

    def _handle_secondary_press(self, current_time: float) -> None:
        """Handle secondary button press event."""
        self.secondary_button_state = True
        self.secondary_press_time = current_time

        # Versuche zuerst die neue secondary Konfiguration zu verwenden
        try:
            secondary_method = self.config.secondary_method
            if "press" in secondary_method or "klick" in secondary_method:
                # Direkte Auslösung bei Press/Klick
                self._trigger_secondary_callback(True)
                return
        except (AttributeError, KeyError, TypeError):
            pass

        # Fallback auf die alten Modi
        if self.secondary_mode == InputMode.SINGLE_CLICK:
            self._trigger_secondary_callback(True)
        elif self.secondary_mode == InputMode.DOUBLE_CLICK:
            self._handle_double_click_secondary(current_time)
        elif self.secondary_mode == InputMode.HOLD:
            self._start_secondary_hold_timer()
        elif self.secondary_mode == InputMode.SMART:
            self._start_secondary_smart_timer()

    def _handle_secondary_release(self, current_time: float) -> None:
        """Handle secondary button release event."""
        self.secondary_button_state = False

        if self.secondary_mode == InputMode.HOLD:
            self._cancel_secondary_hold_timer()
        elif self.secondary_mode == InputMode.SMART:
            self._cancel_secondary_smart_timer()

    def _handle_double_click_primary(self, current_time: float) -> None:
        """Handle double click detection for primary button."""
        # Versuche zuerst die neue primary Konfiguration zu verwenden
        try:
            primary_method = self.config.primary_method
            if "double_click" in primary_method:
                double_click_window = primary_method["double_click"]
            else:
                double_click_window = self.config.input_filter_double_click_window
        except (AttributeError, KeyError, TypeError):
            double_click_window = self.config.input_filter_double_click_window

        if current_time - self.last_primary_click_time < double_click_window:
            # Double click detected
            self.primary_click_count = 0
            self._trigger_primary_callback(True)
            self.logger.debug("Primary button double click detected")
        else:
            # First click, wait for potential second
            self.primary_click_count += 1
            self.last_primary_click_time = current_time

    def _handle_double_click_secondary(self, current_time: float) -> None:
        """Handle double click detection for secondary button."""
        # Versuche zuerst die neue secondary Konfiguration zu verwenden
        try:
            secondary_method = self.config.secondary_method
            if "double_click" in secondary_method:
                double_click_window = secondary_method["double_click"]
            else:
                double_click_window = self.config.input_filter_double_click_window
        except (AttributeError, KeyError, TypeError):
            double_click_window = self.config.input_filter_double_click_window

        if current_time - self.last_secondary_click_time < double_click_window:
            # Double click detected
            self.secondary_click_count = 0
            self._trigger_secondary_callback(True)
            self.logger.debug("Secondary button double click detected")
        else:
            # First click, wait for potential second
            self.secondary_click_count += 1
            self.last_secondary_click_time = current_time

    def _start_primary_hold_timer(self) -> None:
        """Start hold timer for primary button."""
        # Versuche zuerst die neue primary Konfiguration zu verwenden
        try:
            primary_method = self.config.primary_method
            if "hold" in primary_method:
                hold_duration = primary_method["hold"]
            else:
                hold_duration = self.config.input_filter_hold_duration
        except (AttributeError, KeyError, TypeError):
            hold_duration = self.config.input_filter_hold_duration
        
        self.primary_hold_timer = threading.Timer(hold_duration, self._on_primary_hold)
        self.primary_hold_timer.start()

    def _start_secondary_hold_timer(self) -> None:
        """Start hold timer for secondary button."""
        # Versuche zuerst die neue secondary Konfiguration zu verwenden
        try:
            secondary_method = self.config.secondary_method
            if "hold" in secondary_method:
                hold_duration = secondary_method["hold"]
            else:
                hold_duration = self.config.input_filter_hold_duration
        except (AttributeError, KeyError, TypeError):
            hold_duration = self.config.input_filter_hold_duration
        
        self.secondary_hold_timer = threading.Timer(
            hold_duration, self._on_secondary_hold
        )
        self.secondary_hold_timer.start()

    def _cancel_primary_hold_timer(self) -> None:
        """Cancel primary button hold timer."""
        if self.primary_hold_timer:
            self.primary_hold_timer.cancel()
            self.primary_hold_timer = None

    def _cancel_secondary_hold_timer(self) -> None:
        """Cancel secondary button hold timer."""
        if self.secondary_hold_timer:
            self.secondary_hold_timer.cancel()
            self.secondary_hold_timer = None

    def _start_primary_smart_timer(self) -> None:
        """Start smart timer for primary button."""
        # Versuche zuerst die neue primary Konfiguration zu verwenden
        try:
            primary_method = self.config.primary_method
            if "smart" in primary_method:
                smart_delay = primary_method["smart"]
            else:
                smart_delay = self.config.input_filter_smart_delay
        except (AttributeError, KeyError, TypeError):
            smart_delay = self.config.input_filter_smart_delay
        
        self.primary_smart_timer = threading.Timer(smart_delay, self._on_primary_smart)
        self.primary_smart_timer.start()

    def _start_secondary_smart_timer(self) -> None:
        """Start smart timer for secondary button."""
        # Versuche zuerst die neue secondary Konfiguration zu verwenden
        try:
            secondary_method = self.config.secondary_method
            if "smart" in secondary_method:
                smart_delay = secondary_method["smart"]
            else:
                smart_delay = self.config.input_filter_smart_delay
        except (AttributeError, KeyError, TypeError):
            smart_delay = self.config.input_filter_smart_delay
        
        self.secondary_smart_timer = threading.Timer(
            smart_delay, self._on_secondary_smart
        )
        self.secondary_smart_timer.start()

    def _cancel_primary_smart_timer(self) -> None:
        """Cancel primary button smart timer."""
        if self.primary_smart_timer:
            self.primary_smart_timer.cancel()
            self.primary_smart_timer = None

    def _cancel_secondary_smart_timer(self) -> None:
        """Cancel secondary button smart timer."""
        if self.secondary_smart_timer:
            self.secondary_smart_timer.cancel()
            self.secondary_smart_timer = None

    def _on_primary_hold(self) -> None:
        """Callback for primary button hold completion."""
        if self.primary_button_state:  # Still pressed
            self._trigger_primary_callback(True)
            self.logger.debug("Primary button hold completed")

    def _on_secondary_hold(self) -> None:
        """Callback for secondary button hold completion."""
        if self.secondary_button_state:  # Still pressed
            self._trigger_secondary_callback(True)
            self.logger.debug("Secondary button hold completed")

    def _on_primary_smart(self) -> None:
        """Callback for primary button smart detection."""
        if self.primary_button_state:  # Still pressed
            self._trigger_primary_callback(True)
            self.logger.debug("Primary button smart detection completed")

    def _on_secondary_smart(self) -> None:
        """Callback for secondary button smart detection."""
        if self.secondary_button_state:  # Still pressed
            self._trigger_secondary_callback(True)
            self.logger.debug("Secondary button smart detection completed")

    def _trigger_primary_callback(self, value: bool) -> None:
        """Trigger the primary button callback if available."""
        if self.primary_callback:
            try:
                self.primary_callback(value)
            except Exception as e:
                self.logger.error(f"Error in primary callback: {e}")

    def _trigger_secondary_callback(self, value: bool) -> None:
        """Trigger the secondary button callback if available."""
        if self.secondary_callback:
            try:
                self.secondary_callback(value)
            except Exception as e:
                self.logger.error(f"Error in secondary callback: {e}")

    def update_config(self) -> None:
        """Update the filter modes from configuration."""
        self._update_modes()

    def cleanup(self) -> None:
        """Clean up timers and resources."""
        self._cancel_primary_hold_timer()
        self._cancel_secondary_hold_timer()
        self._cancel_primary_smart_timer()
        self._cancel_secondary_smart_timer()
