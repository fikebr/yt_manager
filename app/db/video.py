import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from app.settings import DB_PATH
from app.utils.logger import setup_logging

logger = setup_logging()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the videos table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            video_id TEXT,
            title TEXT,
            channel TEXT,
            duration TEXT,
            file_path TEXT,
            status TEXT DEFAULT 'new',
            download_needed TEXT DEFAULT 'no',
            viewed TEXT DEFAULT 'no',
            error_msg TEXT,
            create_dt TIMESTAMP,
            modified_dt TIMESTAMP,
            published_dt TIMESTAMP,
            download_dt TIMESTAMP,
            view_dt TIMESTAMP,
            delete_dt TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def add_video(url: str, video_id: str) -> int:
    """Adds a new video to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        INSERT INTO videos (url, video_id, status, create_dt, modified_dt)
        VALUES (?, ?, ?, ?, ?)
    ''', (url, video_id, 'new', now, now))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_videos() -> List[Dict[str, Any]]:
    """Retrieves all videos from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos ORDER BY create_dt DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_video_by_id(video_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a video by its primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_video_by_youtube_id(youtube_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a video by its YouTube ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE video_id = ?', (youtube_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_video_status(video_id: int, status: str, error_msg: str = None):
    """Updates the status of a video."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    query = 'UPDATE videos SET status = ?, modified_dt = ?'
    params = [status, now]
    
    if error_msg is not None:
        query += ', error_msg = ?'
        params.append(error_msg)
        
    if status == 'down':
        query += ', download_dt = ?, download_needed = ?'
        params.extend([now, 'down'])
    elif status == 'archive':
         # Keep archive date if moving, or maybe not needed? 
         # PRD says "Moves the file... Updates status to archive"
         pass
    elif status == 'closed':
        query += ', delete_dt = ?'
        params.append(now)

    query += ' WHERE id = ?'
    params.append(video_id)
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def update_video_metadata(video_id: int, title: str, channel: str, duration: str, published_dt: str):
    """Updates the metadata of a video."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        UPDATE videos 
        SET title = ?, channel = ?, duration = ?, published_dt = ?, modified_dt = ?
        WHERE id = ?
    ''', (title, channel, duration, published_dt, now, video_id))
    
    conn.commit()
    conn.close()

def update_video_filepath(video_id: int, file_path: str):
    """Updates the file path of a video."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        UPDATE videos 
        SET file_path = ?, modified_dt = ?
        WHERE id = ?
    ''', (file_path, now, video_id))
    
    conn.commit()
    conn.close()

def update_video_url(video_id: int, url: str):
    """Updates the URL of a video."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        UPDATE videos 
        SET url = ?, modified_dt = ?
        WHERE id = ?
    ''', (url, now, video_id))
    
    conn.commit()
    conn.close()

def mark_video_viewed(video_id: int):
    """Marks a video as viewed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        UPDATE videos 
        SET viewed = 'yes', view_dt = ?, modified_dt = ?
        WHERE id = ?
    ''', (now, now, video_id))
    
    conn.commit()
    conn.close()

def delete_video_record(video_id: int):
    """Deletes a video record from the database (Soft delete per PRD: status=closed)."""
    # PRD: "Deletes the physical file... Updates status to closed... Sets delete_dt"
    # This function maps to that logic DB side.
    update_video_status(video_id, 'closed')
