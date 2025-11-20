import threading
import os
import shutil
import subprocess
import sys
from pathlib import Path
from app.db import video as db
from app.core.google import GoogleManager
from app.core.ytdlp import YTDLPManager
from app.settings import PLAYER_EXE_PATH, ARCHIVE_DIR
from app.utils.logger import setup_logging

logger = setup_logging()

class VideoManager:
    def __init__(self, google_manager: GoogleManager, ytdlp_manager: YTDLPManager):
        self.google = google_manager
        self.ytdlp = ytdlp_manager

    def add_video(self, url: str, video_id: str):
        """Adds a video to the database and starts background processing."""
        logger.info(f"Adding video: {url} (ID: {video_id})")
        v_id = db.add_video(url, video_id)
        db.update_video_status(v_id, 'open')

        # Run background task
        thread = threading.Thread(target=self._process_video, args=(v_id, video_id, url))
        thread.start()

    def _process_video(self, db_id: int, video_id: str, url: str):
        logger.info(f"Processing video {db_id} ({video_id})")
        try:
            # 1. Fetch Metadata
            info = self.google.get_video_info(video_id)
            if info:
                db.update_video_metadata(
                    db_id, 
                    info.get('title', ''), 
                    info.get('channel', ''), 
                    info.get('duration', ''), 
                    info.get('published_dt', '')
                )
                # Update URL to canonical YouTube format
                canonical_url = f"https://www.youtube.com/watch?v={video_id}"
                db.update_video_url(db_id, canonical_url)
                logger.info(f"Updated URL for video {db_id} to canonical format: {canonical_url}")
            
            # 2. Download
            file_path = self.ytdlp.download_video(url, video_id)
            db.update_video_filepath(db_id, file_path)
            db.update_video_status(db_id, 'down')
            logger.info(f"Video {db_id} downloaded successfully.")
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            db.update_video_status(db_id, 'error', str(e))

    def get_all_videos(self):
        return db.get_all_videos()

    def play_video(self, video_id: int):
        video = db.get_video_by_id(video_id)
        if not video or not video['file_path']:
            logger.warning("Video or file not found.")
            return

        file_path = video['file_path']
        if not os.path.exists(file_path):
             logger.error(f"File not found on disk: {file_path}")
             db.update_video_status(video_id, 'error', 'File not found')
             return

        if not PLAYER_EXE_PATH:
            logger.error("Player executable not configured.")
            return

        try:
            logger.info(f'Playing video: "{PLAYER_EXE_PATH}" "{file_path}"')
            subprocess.Popen(f'"{PLAYER_EXE_PATH}" "{file_path}"', shell=True)
            db.mark_video_viewed(video_id)
        except Exception as e:
            logger.error(f"Failed to play video: {e}")

    def delete_video(self, video_id: int):
        video = db.get_video_by_id(video_id)
        if not video:
            return

        file_path = video['file_path']
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file: {e}")
        
        db.delete_video_record(video_id)

    def archive_video(self, video_id: int):
        video = db.get_video_by_id(video_id)
        if not video or not video['file_path']:
            return

        file_path = video['file_path']
        if not os.path.exists(file_path):
            logger.error(f"File not found for archiving: {file_path}")
            return

        try:
            filename = os.path.basename(file_path)
            dest_path = Path(ARCHIVE_DIR) / filename
            shutil.move(file_path, dest_path)
            logger.info(f"Archived file to: {dest_path}")
            
            db.update_video_filepath(video_id, str(dest_path))
            db.update_video_status(video_id, 'archive')
        except Exception as e:
            logger.error(f"Failed to archive file: {e}")
            db.update_video_status(video_id, 'error', f"Archive failed: {e}")

    def mark_download_complete(self, youtube_id: str, file_path: str):
        """Updates the video record upon download completion."""
        logger.info(f"Handling download completion for ID: {youtube_id}")
        
        video = db.get_video_by_youtube_id(youtube_id)
        if not video:
            logger.error(f"Video with YouTube ID {youtube_id} not found in database.")
            return

        db_id = video['id']
        db.update_video_filepath(db_id, file_path)
        db.update_video_status(db_id, 'down')
        logger.info(f"Successfully marked video {db_id} as 'down'.")

    def open_web_url(self, video_id: int):
        """Opens the video URL in the default browser."""
        video = db.get_video_by_id(video_id)
        if not video or not video['url']:
            logger.warning(f"Video {video_id} or URL not found.")
            return

        url = video['url']
        try:
            logger.info(f"Opening URL in browser: {url}")
            # Cross-platform URL opening - let OS decide the browser
            # subprocess.Popen doesn't wait for process output or error codes
            if sys.platform == 'win32':
                subprocess.Popen(f'start "" "{url}"', shell=True)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', url])
            else:
                # Linux and other Unix-like systems
                subprocess.Popen(['xdg-open', url])
        except Exception as e:
            logger.error(f"Failed to open URL in browser: {e}")
