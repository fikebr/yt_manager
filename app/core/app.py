import urllib.parse
import subprocess
from app.db import video as db
from app.core.google import GoogleManager
from app.core.ytdlp import YTDLPManager
from app.core.videos import VideoManager
from app.settings import DB_BROWSER_PATH, DB_PATH, TREESIZE, DOWNLOAD_DIR, ARCHIVE_DIR
from app.utils.logger import setup_logging

logger = setup_logging()

class YTManagerApp:
    def __init__(self):
        self.google = GoogleManager()
        self.ytdlp = YTDLPManager()
        self.video_manager = VideoManager(self.google, self.ytdlp)
        db.init_db()

    # ----------------------------------------------------------------
    # Utility / Shared Logic
    # ----------------------------------------------------------------

    def extract_video_id(self, input_str: str) -> str:
        """Extracts video ID from YouTube URL or returns the input if it's a plain video ID."""
        input_str = input_str.strip()
        
        # First, try to extract from URL
        try:
            parsed = urllib.parse.urlparse(input_str)
            if parsed.hostname == 'youtu.be':
                video_id = parsed.path[1:]
                if video_id:
                    return video_id
            if parsed.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed.path == '/watch':
                    p = urllib.parse.parse_qs(parsed.query)
                    video_id = p.get('v', [None])[0]
                    if video_id:
                        return video_id
        except Exception as e:
            logger.debug(f"Error parsing as URL: {e}")
        
        # If URL parsing failed, check if input looks like a video ID
        # YouTube video IDs are typically 11 characters, alphanumeric + '-' and '_'
        # But we'll be lenient and accept anything that doesn't look like a URL
        if input_str and not input_str.startswith(('http://', 'https://', 'www.')):
            # Check if it looks like a valid video ID (reasonable length, no spaces)
            if len(input_str) >= 8 and len(input_str) <= 20 and ' ' not in input_str:
                logger.info(f"Treating input as plain video ID: {input_str}")
                return input_str
        
        logger.error(f"Could not extract video ID from: {input_str}")
        return None

    def open_db_browser(self):
        if not DB_BROWSER_PATH:
            logger.error("DB Browser path not configured.")
            return
        try:
            logger.info(f"Opening DB Browser: {DB_BROWSER_PATH} with {DB_PATH}")
            subprocess.Popen([DB_BROWSER_PATH, str(DB_PATH)])
        except Exception as e:
            logger.error(f"Failed to open DB Browser: {e}")

    def open_treesize_new(self):
        if not TREESIZE:
            logger.error("TreeSize path not configured.")
            return
        try:
            # Convert forward slashes to backslashes for Windows paths
            treesize_path = TREESIZE.replace('/', '\\')
            download_dir = DOWNLOAD_DIR.replace('/', '\\')
            logger.info(f"Opening TreeSize: {treesize_path} with {download_dir}")
            # Use shell=True to avoid elevation issues on Windows
            subprocess.Popen(f'"{treesize_path}" "{download_dir}"', shell=True)
        except Exception as e:
            logger.error(f"Failed to open TreeSize: {e}")

    def open_treesize_archive(self):
        if not TREESIZE:
            logger.error("TreeSize path not configured.")
            return
        try:
            # Convert forward slashes to backslashes for Windows paths
            treesize_path = TREESIZE.replace('/', '\\')
            archive_dir = ARCHIVE_DIR.replace('/', '\\')
            logger.info(f"Opening TreeSize: {treesize_path} with {archive_dir}")
            # Use shell=True to avoid elevation issues on Windows
            subprocess.Popen(f'"{treesize_path}" "{archive_dir}"', shell=True)
        except Exception as e:
            logger.error(f"Failed to open TreeSize: {e}")

    # ----------------------------------------------------------------
    # Delegate to VideoManager
    # ----------------------------------------------------------------

    def add_video(self, input_str: str):
        """Adds a video by URL or video ID. Constructs canonical URL if needed."""
        input_str = input_str.strip()
        video_id = self.extract_video_id(input_str)
        if not video_id:
            logger.error(f"Invalid URL or video ID: {input_str}")
            return
        
        # If input was a plain video ID, construct the canonical URL
        # Otherwise, use the provided URL
        if input_str.startswith(('http://', 'https://', 'www.')):
            url = input_str
        else:
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"Constructed canonical URL from video ID: {url}")
        
        self.video_manager.add_video(url, video_id)

    def get_all_videos(self):
        return self.video_manager.get_all_videos()

    def play_video(self, video_id: int):
        self.video_manager.play_video(video_id)

    def delete_video(self, video_id: int):
        self.video_manager.delete_video(video_id)

    def archive_video(self, video_id: int):
        self.video_manager.archive_video(video_id)

    def open_web_url(self, video_id: int):
        """Opens the video URL in the default browser."""
        self.video_manager.open_web_url(video_id)