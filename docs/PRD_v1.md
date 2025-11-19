# Product Requirements Document (PRD) - YT Manager v1

## 1. Introduction
**Project Name:** YT Manager
**Version:** v1.0
**Description:** A desktop application to manage a queue of YouTube videos. It allows users to add video URLs, automatically downloads metadata (via Google API) and the video file (via yt-dlp), and provides an interface to play, delete, or archive the downloaded content.

## 2. Goals and Objectives
- Simplify the process of downloading and managing YouTube videos for offline viewing.
- Provide a centralized database of video metadata and file locations.
- enable simple integration with external media players and database tools.

## 3. User Stories & Functional Requirements

### 3.1 Video Management
- **Add Video:** 
  - User can input a YouTube URL into a text field.
  - User clicks "Add Video" to start the process.
  - **System Action:**
    1. Sets status to `open`.
    2. Fetches metadata (title, channel, publication date, duration) using Google YouTube Data API.
    3. Initiates download via `yt-dlp`.
    4. Refreshes the UI table upon completion/update.

- **View Queue:**
  - User sees a list/table of active videos (Status: `new`, `open`, `down`, `error`).
  - Columns displayed: Video ID, Status, Title, Channel.
  - Action buttons per row: Play, Del, Archive.

- **Play Video:**
  - User clicks "Play" on a video row.
  - **System Action:** Opens the downloaded file using the media player executable defined in the application configuration.
  - **System Action:** Updates `viewed` status to `yes` and sets `view_dt`.

- **Delete Video:**
  - User clicks "Del" (Delete) on a video row.
  - **System Action:** 
    - Deletes the physical file from the disk.
    - Updates `status` to `closed`.
    - Sets `delete_dt`.

- **Archive Video:**
  - User clicks "Archive" on a video row.
  - **System Action:**
    - Moves the file to the archive folder defined in the configuration.
    - Updates `status` to `archive`.

### 3.2 System Operations
- **Refresh List:** User can manually refresh the video table to see the latest statuses.
- **Open Database:** User can click a button to open the underlying SQLite database in an external tool ("DB Browser for SQLite").

## 4. User Interface (UI) Requirements
**Screen:** Video Queue (Main Screen)

**Layout:**
1.  **Header/Input Area:**
    -   Text Input: "Video URL Here"
    -   Button: "Add Video"
2.  **Video Table (Queue):**
    -   Rows represent individual video records.
    -   **Columns:**
        -   `Video ID`: Text
        -   `Status`: Text (e.g., Open, Down)
        -   `Title`: Text
        -   `Channel`: Text
        -   **Actions:** 
            -   Button: `Play`
            -   Button: `Del`
            -   Button: `Archive`
3.  **Footer/Controls:**
    -   Button: `Refresh` (Refresh the table view)
    -   Button: `Open DB` (Launch DB Browser with current DB)

## 5. Data Model
**Database:** SQLite
**Table:** `videos` (implied name)

### Fields
| Field Name | Type | Description |
| :--- | :--- | :--- |
| `id` | PK | Unique identifier |
| `url` | String | The YouTube video URL |
| `video_id` | String | YouTube Video ID extracted from URL |
| `title` | String | Video Title (from API) |
| `channel` | String | Channel Name (from API) |
| `duration` | String | Video duration (from API) |
| `file_path` | String | Local path to the downloaded file |
| `status` | Enum | `new` (default), `open`, `down`, `archive`, `closed`, `error` |
| `download_needed` | Enum | `no` (default), `yes`, `down` |
| `viewed` | Enum | `no` (default), `yes` |
| `error_msg` | String | Description of error if status is `error` |
| `create_dt` | DateTime | Record creation timestamp |
| `modified_dt` | DateTime | Last modification timestamp |
| `published_dt` | DateTime | Video publication date (from API) |
| `download_dt` | DateTime | When video was downloaded |
| `view_dt` | DateTime | When video was sent to player |
| `delete_dt` | DateTime | When video was deleted |

### Status Definitions
- **new:** Default upon adding to table.
- **open:** Accepted for processing.
- **down:** File successfully downloaded.
- **archive:** File moved to archive.
- **closed:** Skipped, deleted, or never downloaded.
- **error:** Process failed (API, Network, or File error).

## 6. Technical Architecture & Stack

### 6.1 Technology Stack
-   **Language:** Python
-   **Package Management:** `uv` (User mandate)
-   **Database:** SQLite
-   **GUI Framework:** Tkinter
-   **External APIs:** Google YouTube Data API
-   **Video Downloader:** `yt-dlp` (Executable integration)

### 6.2 Application Structure (Suggested)
```text
yt-manager/
    app/
        __init__.py
        config.py               # Configuration logic
        config/
            ytdlp-config.txt    # Config file for yt-dlp executable
        core/
            videos.py           # Video business logic
            channels.py         # Channel business logic
            app.py              # Orchestrator
            google.py           # Google API wrapper
            ytdlp.py            # yt-dlp wrapper
        db/
            video.py            # DB abstraction layer
            yt-manager.db       # SQLite file
        ui/                     # Tkinter screens/components
        cli/                    # Command-line interface
        utils/
            logger.py           # Logging configuration (File & Screen)
            file_tools.py       # Filesystem operations
            video_player.py     # Media player integration
            open_db.bat         # Helper to open DB Browser
    tests/
    docs/
    pyproject.toml
    README.md
    .env
```

### 6.3 Key Integrations
1.  **yt-dlp:**
    -   The app does not bundle `yt-dlp` but expects it on the system PATH.
    -   The app generates/maintains a config file for `yt-dlp`.
    -   Executes `yt-dlp` via subprocess, passing the config file and the download folder path (from config) as arguments.
    -   Uses a callback/command-line option to capture the final filename/path.

2.  **Google API:**
    -   Used to fetch metadata before downloading.
    -   Requires API Key (likely stored in `.env` or config).

3.  **Logging:**
    -   **Requirement:** Log to both File and Screen (Console).
    -   Must capture errors gracefully.

4.  **Configuration:**
    -   Must store the path to the external video player executable.
    -   Must store the path to the DB Browser executable.
    -   Must store the path for the "New Downloads" folder.
    -   Must store the path for the "Archive" folder.

5.  **Error Handling:**
    -   Graceful error catching for all external interactions (Network, API, File I/O).
    -   Updates video status to `error` and populates `error_msg` instead of crashing.

## 7. Development Standards & Constraints
-   **Module Management:** strictly use `uv`.
-   **Version Control:** `requirements.txt` or `pyproject.toml` should not have pinned versions unless necessary (User preference).
-   **Logging:** Mandatory implementation for all key actions.
-   **Docstrings:** Single simple sentence describing the function.
-   **Testing:** Manual testing by user; no automated test runs required by assistant.

