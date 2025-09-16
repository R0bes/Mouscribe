# src/ui/widgets.py - Mouse overlay widgets for Mauscribe
"""
Dynamic overlay widgets that appear near mouse cursor.
Supports click-and-hold interactions with customizable content.
"""
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Any, Tuple
from enum import Enum
import tkinter as tk
from tkinter import ttk

if sys.platform == "win32":
    try:
        import win32gui
        import win32api
        import win32con
        WINDOWS_API_AVAILABLE = True
    except ImportError:
        WINDOWS_API_AVAILABLE = False
else:
    WINDOWS_API_AVAILABLE = False


class WidgetPosition(Enum):
    """Widget position relative to mouse cursor."""
    TOP_RIGHT = (10, -30)
    TOP_LEFT = (-10, -30)
    BOTTOM_RIGHT = (10, 10)
    BOTTOM_LEFT = (-10, 10)
    RIGHT = (20, -10)
    LEFT = (-20, -10)


class WidgetTheme(Enum):
    """Pre-defined widget themes."""
    DARK = {
        'bg': '#2d2d2d',
        'fg': '#ffffff',
        'border': '#555555',
        'alpha': 0.9
    }
    LIGHT = {
        'bg': '#ffffff',
        'fg': '#000000', 
        'border': '#cccccc',
        'alpha': 0.95
    }
    RECORDING = {
        'bg': '#1a1a2e',
        'fg': '#ff6b6b',
        'border': '#ff4757',
        'alpha': 0.9
    }
    SUCCESS = {
        'bg': '#0f3460',
        'fg': '#2ed573',
        'border': '#2ed573',
        'alpha': 0.9
    }


@dataclass
class WidgetConfig:
    """Configuration for overlay widgets."""
    position: WidgetPosition = WidgetPosition.TOP_RIGHT
    theme: WidgetTheme = WidgetTheme.DARK
    hold_duration: float = 0.5  # seconds to trigger
    fade_duration: float = 0.3  # seconds to fade in/out
    auto_hide_duration: Optional[float] = 3.0  # auto hide after seconds
    click_through: bool = False  # allow clicks to pass through
    always_on_top: bool = True
    border_radius: int = 8
    padding: int = 10


class BaseWidget(ABC):
    """Base class for overlay widgets."""
    
    def __init__(self, config: WidgetConfig = None):
        self.config = config or WidgetConfig()
        self.window: Optional[tk.Toplevel] = None
        self.is_visible = False
        self._fade_thread: Optional[threading.Thread] = None
        self._auto_hide_thread: Optional[threading.Thread] = None
        
    @abstractmethod
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create widget content. Override in subclasses."""
        pass
    
    def show_at_mouse(self) -> bool:
        """Show widget at current mouse position."""
        mouse_pos = self._get_mouse_position()
        if not mouse_pos:
            return False
            
        return self.show_at_position(mouse_pos[0], mouse_pos[1])
    
    def show_at_position(self, x: int, y: int) -> bool:
        """Show widget at specific screen coordinates."""
        try:
            if self.is_visible:
                self.hide()
                
            self._create_window()
            self._position_window(x, y)
            self._apply_styling()
            
            # Create content
            content = self.create_content(self.window)
            content.pack(fill='both', expand=True, padx=self.config.padding, pady=self.config.padding)
            
            # Make window visible
            self.window.deiconify()
            self.window.lift()
            self.window.attributes('-topmost', self.config.always_on_top)
            
            self.is_visible = True
            
            # Start fade in animation
            if self.config.fade_duration > 0:
                self._fade_in()
            else:
                self.window.attributes('-alpha', self.config.theme.value['alpha'])
            
            # Start auto-hide timer
            if self.config.auto_hide_duration:
                self._start_auto_hide()
                
            return True
            
        except Exception as e:
            print(f"Error showing widget: {e}")
            return False
    
    def hide(self) -> None:
        """Hide the widget."""
        if not self.is_visible or not self.window:
            return
            
        self.is_visible = False
        
        # Cancel auto-hide timer
        if self._auto_hide_thread:
            self._auto_hide_thread = None
        
        # Fade out or immediate hide
        if self.config.fade_duration > 0:
            self._fade_out()
        else:
            self._destroy_window()
    
    def update_content(self, **kwargs) -> None:
        """Update widget content. Override in subclasses."""
        pass
    
    def _create_window(self) -> None:
        """Create the overlay window."""
        if not hasattr(self, '_root'):
            self._root = tk.Tk()
            self._root.withdraw()  # Hide root window
            
        self.window = tk.Toplevel(self._root)
        self.window.withdraw()  # Start hidden
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Make window click-through on Windows
        if WINDOWS_API_AVAILABLE and self.config.click_through:
            self.window.update()  # Ensure window exists
            hwnd = self.window.winfo_id()
            extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                 extended_style | win32con.WS_EX_TRANSPARENT)
    
    def _position_window(self, mouse_x: int, mouse_y: int) -> None:
        """Position window relative to mouse cursor."""
        # Update window to get correct size
        self.window.update_idletasks()
        
        offset_x, offset_y = self.config.position.value
        
        # Calculate final position
        final_x = mouse_x + offset_x
        final_y = mouse_y + offset_y
        
        # Keep widget on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        widget_width = self.window.winfo_reqwidth()
        widget_height = self.window.winfo_reqheight()
        
        if final_x + widget_width > screen_width:
            final_x = screen_width - widget_width - 10
        if final_x < 0:
            final_x = 10
        if final_y + widget_height > screen_height:
            final_y = screen_height - widget_height - 10  
        if final_y < 0:
            final_y = 10
            
        self.window.geometry(f"+{final_x}+{final_y}")
    
    def _apply_styling(self) -> None:
        """Apply theme styling to window."""
        theme = self.config.theme.value
        self.window.configure(
            bg=theme['bg'],
            highlightbackground=theme['border'],
            highlightthickness=1
        )
        
        # Set initial alpha to 0 for fade-in effect
        self.window.attributes('-alpha', 0.0 if self.config.fade_duration > 0 else theme['alpha'])
    
    def _get_mouse_position(self) -> Optional[Tuple[int, int]]:
        """Get current mouse cursor position."""
        try:
            if WINDOWS_API_AVAILABLE:
                point = win32gui.GetCursorPos()
                return point
            else:
                # Fallback for other platforms
                root = tk.Tk()
                root.withdraw()
                x = root.winfo_pointerx()
                y = root.winfo_pointery()
                root.destroy()
                return (x, y)
        except Exception:
            return None
    
    def _fade_in(self) -> None:
        """Fade in animation."""
        if self._fade_thread:
            return
            
        target_alpha = self.config.theme.value['alpha']
        duration = self.config.fade_duration
        
        def fade():
            steps = 20
            step_duration = duration / steps
            alpha_step = target_alpha / steps
            
            for i in range(steps):
                if not self.is_visible or not self.window:
                    return
                try:
                    alpha = alpha_step * (i + 1)
                    self.window.attributes('-alpha', alpha)
                    time.sleep(step_duration)
                except tk.TclError:
                    return
                    
        self._fade_thread = threading.Thread(target=fade, daemon=True)
        self._fade_thread.start()
    
    def _fade_out(self) -> None:
        """Fade out animation."""
        def fade():
            if not self.window:
                return
                
            try:
                current_alpha = self.window.attributes('-alpha')
                steps = 15
                duration = self.config.fade_duration
                step_duration = duration / steps
                alpha_step = current_alpha / steps
                
                for i in range(steps):
                    if not self.window:
                        return
                    alpha = current_alpha - (alpha_step * (i + 1))
                    self.window.attributes('-alpha', max(0, alpha))
                    time.sleep(step_duration)
                    
                self._destroy_window()
            except tk.TclError:
                self._destroy_window()
                
        threading.Thread(target=fade, daemon=True).start()
    
    def _start_auto_hide(self) -> None:
        """Start auto-hide timer."""
        def auto_hide():
            time.sleep(self.config.auto_hide_duration)
            if self.is_visible:
                self.hide()
                
        self._auto_hide_thread = threading.Thread(target=auto_hide, daemon=True)
        self._auto_hide_thread.start()
    
    def _destroy_window(self) -> None:
        """Destroy the window."""
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None


class TextWidget(BaseWidget):
    """Simple text display widget."""
    
    def __init__(self, text: str = "Text", config: WidgetConfig = None):
        super().__init__(config)
        self.text = text
        self._label: Optional[tk.Label] = None
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create text label."""
        theme = self.config.theme.value
        
        self._label = tk.Label(
            parent,
            text=self.text,
            bg=theme['bg'],
            fg=theme['fg'],
            font=('Segoe UI', 10),
            justify='left'
        )
        return self._label
    
    def update_content(self, text: str = None, **kwargs) -> None:
        """Update displayed text."""
        if text:
            self.text = text
        if self._label:
            self._label.configure(text=self.text)


class RecordingWidget(BaseWidget):
    """Widget for recording status with animated indicator."""
    
    def __init__(self, config: WidgetConfig = None):
        if not config:
            config = WidgetConfig(theme=WidgetTheme.RECORDING)
        super().__init__(config)
        
        self.recording_time = 0.0
        self._frame: Optional[tk.Frame] = None
        self._status_label: Optional[tk.Label] = None
        self._time_label: Optional[tk.Label] = None
        self._indicator: Optional[tk.Label] = None
        self._animation_running = False
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create recording widget content."""
        theme = self.config.theme.value
        
        self._frame = tk.Frame(parent, bg=theme['bg'])
        
        # Recording indicator (pulsing dot)
        self._indicator = tk.Label(
            self._frame,
            text="●",
            bg=theme['bg'],
            fg=theme['fg'],
            font=('Segoe UI', 16)
        )
        self._indicator.pack(side='left', padx=(0, 5))
        
        # Status text
        self._status_label = tk.Label(
            self._frame,
            text="Recording...",
            bg=theme['bg'],
            fg=theme['fg'],
            font=('Segoe UI', 10, 'bold')
        )
        self._status_label.pack(side='left', padx=(0, 10))
        
        # Time display
        self._time_label = tk.Label(
            self._frame,
            text="00:00",
            bg=theme['bg'],
            fg=theme['fg'],
            font=('Segoe UI Mono', 10)
        )
        self._time_label.pack(side='left')
        
        # Start animation
        self._start_pulse_animation()
        
        return self._frame
    
    def update_content(self, recording_time: float = None, **kwargs) -> None:
        """Update recording time."""
        if recording_time is not None:
            self.recording_time = recording_time
            
        if self._time_label:
            minutes = int(self.recording_time // 60)
            seconds = int(self.recording_time % 60)
            self._time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
    
    def _start_pulse_animation(self) -> None:
        """Start pulsing animation for recording indicator."""
        self._animation_running = True
        
        def pulse():
            colors = ['#ff4757', '#ff6b6b', '#ff8a8a', '#ff6b6b']
            i = 0
            
            while self._animation_running and self._indicator:
                try:
                    self._indicator.configure(fg=colors[i % len(colors)])
                    i += 1
                    time.sleep(0.3)
                except tk.TclError:
                    break
                    
        threading.Thread(target=pulse, daemon=True).start()
    
    def hide(self) -> None:
        """Stop animation and hide widget."""
        self._animation_running = False
        super().hide()


class MouseOverlayManager:
    """Manager for mouse overlay widgets with hold-to-show functionality."""
    
    def __init__(self):
        self.widgets = {}
        self._hold_timers = {}
        self._mouse_monitor_active = False
        self._last_mouse_pos = None
        
        # Windows-specific mouse hook
        if WINDOWS_API_AVAILABLE:
            self._setup_mouse_hook()
    
    def register_widget(self, name: str, widget: BaseWidget, 
                       trigger_button: str = 'left',
                       hold_duration: float = 0.5) -> None:
        """Register a widget with hold-to-show trigger."""
        self.widgets[name] = {
            'widget': widget,
            'trigger_button': trigger_button,
            'hold_duration': hold_duration
        }
    
    def show_widget(self, name: str, x: int = None, y: int = None) -> bool:
        """Show widget by name at position or mouse cursor."""
        if name not in self.widgets:
            return False
            
        widget = self.widgets[name]['widget']
        
        if x is not None and y is not None:
            return widget.show_at_position(x, y)
        else:
            return widget.show_at_mouse()
    
    def hide_widget(self, name: str) -> None:
        """Hide widget by name."""
        if name in self.widgets:
            self.widgets[name]['widget'].hide()
    
    def hide_all(self) -> None:
        """Hide all widgets."""
        for widget_info in self.widgets.values():
            widget_info['widget'].hide()
    
    def _setup_mouse_hook(self) -> None:
        """Setup Windows mouse hook for hold detection."""
        # This would require more complex Windows API integration
        # For now, we'll use a polling-based approach
        self._start_mouse_polling()
    
    def _start_mouse_polling(self) -> None:
        """Start polling mouse state (simplified approach)."""
        def poll_mouse():
            while True:
                # This is a simplified version
                # In practice, you'd want proper mouse hook integration
                time.sleep(0.05)  # 20 FPS polling
                
        if not self._mouse_monitor_active:
            self._mouse_monitor_active = True
            threading.Thread(target=poll_mouse, daemon=True).start()


# Convenience functions
def create_text_widget(text: str, theme: WidgetTheme = WidgetTheme.DARK,
                      position: WidgetPosition = WidgetPosition.TOP_RIGHT) -> TextWidget:
    """Create a simple text widget."""
    config = WidgetConfig(theme=theme, position=position)
    return TextWidget(text, config)


def create_recording_widget(position: WidgetPosition = WidgetPosition.TOP_RIGHT) -> RecordingWidget:
    """Create a recording status widget."""
    config = WidgetConfig(
        theme=WidgetTheme.RECORDING,
        position=position,
        auto_hide_duration=None  # Don't auto-hide recording widget
    )
    return RecordingWidget(config)


# Example usage
if __name__ == "__main__":
    # Create overlay manager
    manager = MouseOverlayManager()
    
    # Create and register widgets
    text_widget = create_text_widget("🎙️ Hold to record", WidgetTheme.DARK)
    recording_widget = create_recording_widget()
    
    manager.register_widget("prompt", text_widget, "left", 0.5)
    manager.register_widget("recording", recording_widget)
    
    # Show text widget for demo
    manager.show_widget("prompt")
    
    # Keep alive for testing
    input("Press Enter to exit...")
    manager.hide_all()