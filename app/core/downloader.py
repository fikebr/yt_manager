import threading
import time
from app.db import video as db
from app.core.ytdlp import YTDLPManager
from app.settings import CONCURRENT_DOWNLOADS
from app.utils.logger import setup_logging

logger = setup_logging()

class DownloadManager:
    """Manages concurrent video downloads with a limit."""
    
    def __init__(self, ytdlp_manager: YTDLPManager):
        self.ytdlp = ytdlp_manager
        self.running = False
        self.thread = None
        self.lock = threading.Lock()  # For thread-safe start/stop
        self.check_interval = 30  # 30 seconds when active (much shorter)
        
    def start_if_needed(self):
        """Starts the download manager if there's work to do and it's not already running."""
        with self.lock:
            if self.running:
                return  # Already running
            
            # Check if there's any work to do
            queued_count = db.count_videos_by_download_needed('yes')
            downloading_count = db.count_videos_by_download_needed('downloading')
            
            if queued_count == 0 and downloading_count == 0:
                logger.debug("No downloads queued or in progress, DownloadManager not needed")
                return
            
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("DownloadManager started.")
    
    def stop(self):
        """Stops the download manager."""
        with self.lock:
            if not self.running:
                return
            self.running = False
            if self.thread:
                self.thread.join(timeout=10)
            logger.info("DownloadManager stopped.")
    
    def _run(self):
        """Main loop that manages downloads."""
        while self.running:
            try:
                self._process_downloads()
                
                # Check if we should continue running
                queued_count = db.count_videos_by_download_needed('yes')
                downloading_count = db.count_videos_by_download_needed('downloading')
                
                # If nothing to do, shut down
                if queued_count == 0 and downloading_count == 0:
                    logger.info("No more downloads to process, shutting down DownloadManager")
                    self.running = False
                    break
                
                # Sleep for check_interval seconds (shorter when active)
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error in DownloadManager loop: {e}")
                time.sleep(60)  # Wait a minute before retrying on error
    
    def _process_downloads(self):
        """Processes pending downloads up to the concurrent limit."""
        # Count currently downloading videos
        downloading_count = db.count_videos_by_download_needed('downloading')
        logger.debug(f"Currently downloading: {downloading_count}/{CONCURRENT_DOWNLOADS}")
        
        # If we have fewer than the limit downloading, start more
        if downloading_count < CONCURRENT_DOWNLOADS:
            slots_available = CONCURRENT_DOWNLOADS - downloading_count
            
            # Get videos queued for download
            queued_videos = db.get_videos_by_download_needed('yes', limit=slots_available)
            
            if queued_videos:
                logger.info(f"Starting {len(queued_videos)} download(s)")
                
                for video in queued_videos:
                    self._start_download(video)
    
    def _start_download(self, video: dict):
        """Starts a download for a single video."""
        video_id = video['id']
        youtube_id = video['video_id']
        url = video['url']
        
        if not url or not youtube_id:
            logger.error(f"Video {video_id} missing URL or video_id, skipping download")
            db.set_download_needed(video_id, 'no')
            db.update_video_status(video_id, 'error', 'Missing URL or video_id')
            return
        
        try:
            # Mark as downloading
            db.set_download_needed(video_id, 'downloading')
            logger.info(f"Starting download for video {video_id} ({youtube_id})")
            
            # Start download in a separate thread (non-blocking)
            thread = threading.Thread(
                target=self._download_video,
                args=(video_id, youtube_id, url),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting download for video {video_id}: {e}")
            db.set_download_needed(video_id, 'yes')  # Put back in queue
            db.update_video_status(video_id, 'error', str(e))
    
    def _download_video(self, video_id: int, youtube_id: str, url: str):
        """Downloads a video. This runs in a separate thread."""
        try:
            logger.info(f"Downloading video {video_id} ({youtube_id})")
            # This will spawn a subprocess that runs independently
            # The callback from yt-dlp will mark it as complete
            self.ytdlp.download_video(url, youtube_id)
            # Note: We don't update status here because the yt-dlp callback
            # will handle that via mark_download_complete
        except Exception as e:
            logger.error(f"Download failed for video {video_id} ({youtube_id}): {e}")
            # Reset to 'yes' so it can be retried, or set to 'no' if we don't want retries
            db.set_download_needed(video_id, 'yes')
            db.update_video_status(video_id, 'error', str(e))

