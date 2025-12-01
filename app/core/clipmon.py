import threading
import time
import pyperclip
from typing import Optional, Callable
from app.utils.logger import setup_logging

logger = setup_logging()

class ClipboardMonitor:
    """Monitors clipboard for YouTube URLs and adds them to the video queue."""
    
    def __init__(self, app_logic, callback: Optional[Callable[[str], None]] = None):
        """
        Initialize clipboard monitor.
        
        Args:
            app_logic: YTManagerApp instance for adding videos
            callback: Optional callback function to call when URL is detected (for UI updates)
        """
        self.app_logic = app_logic
        self.callback = callback
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_clipboard = ""
        self.check_interval = 1.0  # Check every 1 second
        
    def start(self):
        """Start monitoring clipboard in a background thread."""
        if self.monitoring:
            logger.warning("Clipboard monitor is already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Clipboard monitor started")
    
    def stop(self):
        """Stop monitoring and wait for thread to finish."""
        if not self.monitoring:
            logger.warning("Clipboard monitor is not running")
            return
        
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        logger.info("Clipboard monitor stopped")
    
    def check_clipboard(self):
        """Check clipboard for YouTube URLs and add them if found."""
        try:
            current = pyperclip.paste()
            
            # Only process if clipboard content changed
            if current != self.last_clipboard:
                self.last_clipboard = current
                
                # Check if it's a YouTube URL
                if self._is_youtube_url(current):
                    logger.info(f"Detected YouTube URL in clipboard: {current}")
                    self.add_url(current)
                    
        except pyperclip.PyperclipException as e:
            # Clipboard might be empty or contain non-text
            logger.debug(f"Clipboard access error (non-text or empty): {e}")
        except Exception as e:
            logger.error(f"Error checking clipboard: {e}")
    
    def _is_youtube_url(self, text: str) -> bool:
        """Check if text contains a YouTube URL."""
        
        if not text or not isinstance(text, str):
            return False
        
        text = text.strip()
        if not text:
            return False
        
        # Check for common YouTube URL patterns
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/embed',
            'youtube.com/shorts'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in youtube_patterns)
    
    def add_url(self, url: str):
        """
        Add YouTube URL to video queue.
        
        Args:
            url: YouTube URL to add
        """
        try:
            logger.info(f"Adding URL from clipboard: {url}")
            self.app_logic.add_video(url)
            
            # Call callback if provided (for UI updates)
            if self.callback:
                try:
                    self.callback(url)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error adding URL from clipboard: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in background thread."""
        logger.info("Clipboard monitor loop started")
        
        while self.monitoring:
            try:
                self.check_clipboard()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            # Sleep for check interval
            time.sleep(self.check_interval)
        
        logger.info("Clipboard monitor loop stopped")

