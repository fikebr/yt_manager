import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from app.core.clipmon import ClipboardMonitor
from app.core.app import YTManagerApp
from app.utils.logger import setup_logging

logger = setup_logging()

class ClipboardMonitorWindow(tk.Toplevel):
    """Window for monitoring clipboard and displaying detected YouTube URLs."""
    
    def __init__(self, parent, app_logic: YTManagerApp, on_close_callback: Optional[Callable[[], None]] = None):
        """
        Initialize clipboard monitor window.
        
        Args:
            parent: Parent window (MainWindow)
            app_logic: YTManagerApp instance
            on_close_callback: Optional callback to call when window closes
        """
        super().__init__(parent)
        self.app_logic = app_logic
        self.on_close_callback = on_close_callback
        self.clipboard_monitor: Optional[ClipboardMonitor] = None
        
        self.title("Clipboard Monitor")
        self.geometry("600x400")
        
        # Set up window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._create_widgets()
        self._start_monitoring()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Top frame with label
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Label(
            top_frame, 
            text="Detected YouTube URLs:", 
            font=("Arial", 10, "bold")
        ).pack(side="left")
        
        # Middle frame with Listbox and scrollbar
        mid_frame = ttk.Frame(self, padding=10)
        mid_frame.pack(fill="both", expand=True)
        
        # Listbox for displaying URLs
        listbox_frame = ttk.Frame(mid_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.url_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.url_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.url_listbox.yview)
        
        # Bottom frame with close button
        bot_frame = ttk.Frame(self, padding=10)
        bot_frame.pack(fill="x")
        
        close_btn = ttk.Button(
            bot_frame, 
            text="Close", 
            command=self.on_closing
        )
        close_btn.pack(side="right", padx=5)
    
    def _on_url_detected(self, url: str):
        """
        Callback when URL is detected in clipboard.
        
        Args:
            url: Detected YouTube URL
        """
        try:
            # Add URL to listbox
            self.url_listbox.insert(tk.END, url)
            # Auto-scroll to bottom
            self.url_listbox.see(tk.END)
            logger.info(f"Added URL to listbox: {url}")
        except Exception as e:
            logger.error(f"Error adding URL to listbox: {e}")
    
    def _start_monitoring(self):
        """Start clipboard monitoring."""
        try:
            self.clipboard_monitor = ClipboardMonitor(
                self.app_logic,
                callback=self._on_url_detected
            )
            self.clipboard_monitor.start()
            logger.info("Clipboard monitoring started")
        except Exception as e:
            logger.error(f"Error starting clipboard monitor: {e}")
    
    def on_closing(self):
        """Handle window closing - stop monitoring and destroy window."""
        try:
            if self.clipboard_monitor:
                self.clipboard_monitor.stop()
                logger.info("Clipboard monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping clipboard monitor: {e}")
        
        # Call parent callback if provided
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                logger.error(f"Error in close callback: {e}")
        
        self.destroy()

