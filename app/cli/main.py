import argparse
import sys
from app.core.google import GoogleManager
from app.core.ytdlp import YTDLPManager
from app.core.videos import VideoManager
from app.utils.logger import setup_logging

logger = setup_logging(name="yt_manager_cli")

def handle_downloaded(video_id: str, file_path: str):
    """Handles the download completion callback."""
    # Instantiate managers
    google = GoogleManager()
    ytdlp = YTDLPManager()
    vm = VideoManager(google, ytdlp)
    
    # Delegate to VideoManager
    vm.mark_download_complete(video_id, file_path)

def main():
    parser = argparse.ArgumentParser(description="YT Manager CLI")
    
    # Command flag
    parser.add_argument('--downloaded', action='store_true', help="Flag to indicate a download completion callback")
    
    # Parameters
    parser.add_argument('--videoid', type=str, help="The YouTube Video ID")
    parser.add_argument('--file_path', type=str, help="The downloaded file path")

    args = parser.parse_args()

    if args.downloaded:
        if not args.videoid or not args.file_path:
            logger.error("--videoid and --file_path are required with --downloaded")
            sys.exit(1)
            
        handle_downloaded(args.videoid, args.file_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
