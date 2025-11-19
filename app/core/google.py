from googleapiclient.discovery import build
from app.settings import YT_API_KEY
from app.utils.logger import setup_logging

logger = setup_logging()

class GoogleManager:
    def __init__(self):
        self.api_key = YT_API_KEY
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google API: {e}")

    def get_video_info(self, video_id: str) -> dict:
        """Fetches video metadata from YouTube API."""
        if not self.youtube:
            logger.error("Google API not initialized.")
            return {}

        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails",
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                logger.warning(f"No video found for ID: {video_id}")
                return {}

            item = response['items'][0]
            snippet = item['snippet']
            content_details = item['contentDetails']

            return {
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'published_dt': snippet['publishedAt'],
                'duration': content_details['duration']
            }
        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            return {}

