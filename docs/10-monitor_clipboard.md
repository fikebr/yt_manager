# Monitor Clipboard for URLs

monitor the clipboard if you find a youtube url then add that url to the video-queue

## core.clipmon

the core.clipboard module encompases all of the logic of monitoring the clipboard.

### methods

start: starts a loop in a seperate thread that monitors the clipboard, checks for youtube urls and adds them to the queue then sleeps for X seconds and starts over

stop: stops the loop and releases the thread

check_clipboard: looks at the clipboard for text and checks if that text is a yourube url. if yes then add_url

_is_youtube_url: input text. if the input text is a youtube url then returns true (else false)

add_url: passes the url to the core.videos add_video method


## ui.clipmon

a tk window that starts core.clipmon and stops it when the wondow closes. there is a listview that lists the urls as they are found. there is a button that closes the window at the bottom on the window

## other changes

1) add a button to the video-queue window to open this clipmon window
2) add the pyperclip module


## sample code...

``` python
def __init__(self, app_logic: YTManagerApp):

    self.last_clipboard = ""
    self.clipboard_monitoring = True
    self._start_clipboard_monitor()

def _start_clipboard_monitor(self):
    """Start monitoring clipboard for YouTube URLs."""
    if self.clipboard_monitoring:
        try:
            current = self.clipboard_get()
            if current != self.last_clipboard:
                self.last_clipboard = current
                # Check if it's a YouTube URL
                if self._is_youtube_url(current):
                    logger.info(f"Detected YouTube URL in clipboard: {current}")
                    self.url_var.set(current)
                    # Optionally auto-add: self.add_video()
        except tk.TclError:
            # Clipboard might be empty or contain non-text
            pass
        except Exception as e:
            logger.error(f"Error checking clipboard: {e}")
        
        # Check every 500ms
        self.after(500, self._start_clipboard_monitor)

def _is_youtube_url(self, text: str) -> bool:
    """Check if text contains a YouTube URL."""
    if not text or not isinstance(text, str):
        return False
    text = text.strip()
    return any(domain in text.lower() for domain in [
        'youtube.com/watch', 'youtu.be/', 'youtube.com/embed'
    ])

```