import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "app" / "db" / "yt-manager.db"

# Paths from Env
YT_API_KEY = os.getenv("YT_API_KEY", "")
PLAYER_EXE_PATH = os.getenv("PLAYER_EXE_PATH", r"E:\PortableApps\PortableApps\MPC-BEPortable\MPC-BEPortable.exe")
DB_BROWSER_PATH = os.getenv("DB_BROWSER_PATH", r"E:\PortableApps\PortableApps\SQLiteDatabaseBrowserPortable\SQLiteDatabaseBrowserPortable.exe")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", r"N:/Videos/_New/fromMPC")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", r"N:\Videos\_fromMPC")

# YTDLP Config Path
YTDLP_CONFIG_PATH = BASE_DIR / "app" / "config" / "ytdlp-config.txt"

# Ensure directories exist
Path(DOWNLOAD_DIR).mkdir(exist_ok=True)
Path(ARCHIVE_DIR).mkdir(exist_ok=True)

