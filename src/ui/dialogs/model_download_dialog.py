"""
Model Download Dialog

This module provides a GUI dialog for downloading Whisper models
with progress indication and user confirmation.
"""

import threading
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from src.utils.model_downloader import ModelDownloader


class ModelDownloadDialog:
    """Dialog for downloading Whisper models."""

    def __init__(self, model_id: str, parent_window=None):
        """
        Initialize the download dialog.

        Args:
            model_id: Model identifier to download
            parent_window: Parent window for the dialog
        """
        self.model_id = model_id
        self.downloader = ModelDownloader()
        self.downloading = False
        self.cancelled = False
        self.success = False

        # Get model info
        model_info = self.downloader.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found in configuration")

        self.url, self.size_mb = model_info
        self.description = self.downloader.get_model_descriptions().get(model_id, model_id)

        # Create dialog
        self.dialog = ctk.CTkToplevel(parent_window)
        self.dialog.title(f"Download {model_id.capitalize()} Model")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)

        # Make dialog modal
        self.dialog.transient(parent_window)
        self.dialog.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create the dialog widgets."""
        # Title
        title_label = ctk.CTkLabel(self.dialog, text="Download Whisper Model", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)

        # Model description
        desc_label = ctk.CTkLabel(self.dialog, text=self.description, font=ctk.CTkFont(size=14))
        desc_label.pack(pady=10)

        # Size info
        size_label = ctk.CTkLabel(self.dialog, text=f"Size: {self.size_mb} MB", font=ctk.CTkFont(size=12))
        size_label.pack()

        # Status label
        self.status_label = ctk.CTkLabel(self.dialog, text="Ready to download", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.dialog, width=400, height=20, mode="determinate")
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.dialog)
        buttons_frame.pack(side="bottom", pady=20)

        # Download button
        self.download_button = ctk.CTkButton(buttons_frame, text="Start Download", command=self._start_download, width=120)
        self.download_button.pack(side="left", padx=10)

        # Cancel button
        self.cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self._cancel, width=120, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)

    def _start_download(self):
        """Start the download in a separate thread."""
        self.download_button.configure(state="disabled")
        self.downloading = True
        self.cancelled = False

        # Run download in thread to avoid blocking UI
        thread = threading.Thread(target=self._download_thread)
        thread.daemon = True
        thread.start()

    def _download_thread(self):
        """Download the model in a background thread."""

        def progress_callback(current: int, total: int):
            """Update progress on the UI thread."""
            if total > 0:
                progress = current / total
                self.dialog.after(0, lambda: self.progress_bar.set(progress))

                # Update status
                downloaded_mb = current / (1024 * 1024)
                status_text = f"Downloading... {downloaded_mb:.1f} MB / {self.size_mb} MB"
                self.dialog.after(0, lambda: self.status_label.configure(text=status_text))

        try:
            self.dialog.after(0, lambda: self.status_label.configure(text="Starting download..."))

            # Download the model
            success = self.downloader.download_model(self.model_id, progress_callback)

            if success and not self.cancelled:
                self.success = True
                self.dialog.after(0, lambda: self.status_label.configure(text="Download complete!"))
                self.dialog.after(500, self._close)
            else:
                if self.cancelled:
                    self.dialog.after(0, lambda: self.status_label.configure(text="Download cancelled"))
                else:
                    self.dialog.after(0, lambda: self.status_label.configure(text="Download failed"))

        except Exception as ex:
            error_msg = str(ex)
            self.dialog.after(0, lambda msg=error_msg: self.status_label.configure(text=f"Error: {msg}"))

        finally:
            self.downloading = False
            self.dialog.after(0, lambda: self.cancel_button.configure(state="normal", text="Close"))

    def _cancel(self):
        """Cancel the download."""
        if self.downloading:
            self.cancelled = True
            self.status_label.configure(text="Cancelling download...")
            self.cancel_button.configure(state="disabled")
        else:
            self._close()

    def _close(self):
        """Close the dialog."""
        self.dialog.destroy()

    def show(self) -> bool:
        """
        Show the dialog and wait for completion.

        Returns:
            True if download was successful, False otherwise
        """
        # Center the dialog on the screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Wait for dialog to close
        self.dialog.wait_window()

        return self.success


def show_model_download_dialog(model_id: str, parent_window=None) -> bool:
    """
    Show a model download dialog.

    Args:
        model_id: Model identifier to download
        parent_window: Parent window for the dialog

    Returns:
        True if download was successful, False otherwise
    """
    dialog = ModelDownloadDialog(model_id, parent_window)
    return dialog.show()
