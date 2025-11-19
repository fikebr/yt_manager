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

    def extract_video_id(self, url: str) -> str:
        """Extracts video ID from YouTube URL."""
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.hostname == 'youtu.be':
                return parsed.path[1:]
            if parsed.hostname in ('www.youtube.com', 'youtube.com'):
                if parsed.path == '/watch':
                    p = urllib.parse.parse_qs(parsed.query)
                    return p.get('v', [None])[0]
        except Exception as e:
            logger.error(f"Error extracting ID from {url}: {e}")
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

    def add_video(self, url: str):
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.error(f"Invalid URL or could not extract ID: {url}")
            return
        self.video_manager.add_video(url, video_id)

    def get_all_videos(self):
        return self.video_manager.get_all_videos()

    def play_video(self, video_id: int):
        self.video_manager.play_video(video_id)

    def delete_video(self, video_id: int):
        self.video_manager.delete_video(video_id)

    def archive_video(self, video_id: int):
        self.video_manager.archive_video(video_id)
