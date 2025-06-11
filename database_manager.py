import sqlite3
import hashlib
import os

# Connect to the SQLite database
# Create a database file if it doesn't exist
DB_PATH = 'harmonyhaven_music.db'


def connect_db():
    """Establish a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_music_table():
    """Create the music table if it doesn't exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        md5_hash TEXT,
        title TEXT,
        artist TEXT,
        album TEXT,
        genre TEXT,
        year INTEGER
    )
    """)
    conn.commit()
    conn.close()


def calculate_md5(file_path):
    """Calculate the MD5 hash for a given file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def insert_into_db(file_path, title, artist, album, genre, year):
    """Insert a new music file into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    md5_hash = calculate_md5(file_path)
    try:
        cursor.execute("""
        INSERT INTO music (file_path, md5_hash, title, artist, album, genre, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_path, md5_hash, title, artist, album, genre, year))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"File {file_path} already exists in the database.")
    finally:
        conn.close()


def search_for_song(title):
    """Search for a song in the database by title."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT file_path, artist, album, genre, year
    FROM music
    WHERE title LIKE ?
    """, (f'%{title}%',))
    results = cursor.fetchall()
    conn.close()
    return results


def find_duplicates():
    """Find duplicate files by comparing MD5 hashes."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT file_path, md5_hash
    FROM music
    """)
    files = cursor.fetchall()
    conn.close()

    # Check for duplicates
    hash_map = {}
    duplicates = []
    for file_path, md5_hash in files:
        if md5_hash in hash_map:
            duplicates.append((file_path, hash_map[md5_hash]))
        else:
            hash_map[md5_hash] = file_path

    return duplicates


def delete_song_from_db(file_path):
    """Delete a song from the database based on the file path."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM music
    WHERE file_path = ?
    """, (file_path,))
    conn.commit()
    conn.close()


# Initialize the database and create the table if it doesn't exist
create_music_table()
