import subprocess
import os
import sys
from pathlib import Path
from app.settings import YTDLP_CONFIG_PATH, DOWNLOAD_DIR, BASE_DIR
from app.utils.logger import setup_logging

logger = setup_logging()

class YTDLPManager:
    def download_video(self, url: str, video_id: str) -> str:
        """Downloads the video using yt-dlp and returns the file path."""
        try:
            # 1. Get the filename first
            
            cmd_common = [
                "yt-dlp",
                "--config-location", str(YTDLP_CONFIG_PATH),
                "--paths", f"home:{DOWNLOAD_DIR}", # Combine key and value
            ]
            
            cmd_get_filename = cmd_common + ["--print", "filename", url]
            
            logger.info(f"Resolving filename for {url}")
            result = subprocess.run(cmd_get_filename, capture_output=True, text=True, check=True)
            file_path = result.stdout.strip()
            
            # 2. Download the video with exec callback
            # Use the batch file wrapper to handle quoting and environment
            callback_bat = BASE_DIR / "run_callback.bat"
            
            # We wrap video_id in quotes to prevent issues if it starts with a dash
            # However, argparse might still treat it as a flag if we are not careful.
            # The safest way to pass an argument starting with - to argparse is using key=value syntax:
            # --videoid=VALUE
            
            exec_cmd = f'"{callback_bat}" --downloaded --videoid="{video_id}" --file_path {{}}'
            
            cmd_download = cmd_common + ["--exec", exec_cmd, url]
            
            logger.info(f"Downloading {url} with callback...")
            subprocess.run(cmd_download, check=True)
            
            # Verify file exists
            if not os.path.exists(file_path):
                logger.warning(f"Expected file {file_path} not found after download.")
                
            return file_path

        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp error: {e.stderr if e.stderr else e}")
            raise e
        except Exception as e:
            logger.error(f"Error in download: {e}")
            raise e
