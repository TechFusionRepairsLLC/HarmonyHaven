import sqlite3
import hashlib
import os
from contextlib import contextmanager

# ─── Config ───────────────────────────────────────────────────────────────────
DB_PATH = 'harmonyhaven_music.db'

# ─── Connection ───────────────────────────────────────────────────────────────
@contextmanager
def get_db():
    """
    Context-manager for safe DB access.
    Automatically commits on success and rolls back on error.

    Usage:
        with get_db() as cursor:
            cursor.execute(...)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows act like dicts: row["title"]
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─── Schema ───────────────────────────────────────────────────────────────────
def create_music_table():
    """Create the music table (and indexes) if they don't exist."""
    with get_db() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS music (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path  TEXT    UNIQUE NOT NULL,
            md5_hash   TEXT,
            title      TEXT,
            artist     TEXT,
            album      TEXT,
            genre      TEXT,
            year       INTEGER
        )
        """)
        # Indexes speed up the search queries used by the UI
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_title  ON music (title  COLLATE NOCASE)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_artist ON music (artist COLLATE NOCASE)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_genre  ON music (genre  COLLATE NOCASE)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_hash   ON music (md5_hash)")


# ─── Hashing ──────────────────────────────────────────────────────────────────
def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
    """Return the MD5 hex-digest of a file."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# ─── Insert ───────────────────────────────────────────────────────────────────
def insert_into_db(file_path: str, title: str = "", artist: str = "",
                   album: str = "", genre: str = "", year: int = None) -> bool:
    """
    Insert one music file.  Returns True on success, False if already present.
    """
    md5 = calculate_md5(file_path)
    try:
        with get_db() as cursor:
            cursor.execute("""
                INSERT INTO music (file_path, md5_hash, title, artist, album, genre, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (file_path, md5, title, artist, album, genre, year))
        return True
    except sqlite3.IntegrityError:
        # file_path already exists (UNIQUE constraint)
        return False


def bulk_insert(records: list[dict]) -> tuple[int, int]:
    """
    Insert many records at once — far faster than calling insert_into_db() in a loop.

    Each record is a dict with keys:
        file_path (required), title, artist, album, genre, year

    Returns (inserted_count, skipped_count).
    """
    inserted = skipped = 0
    rows = []
    for rec in records:
        fp = rec.get("file_path", "")
        if not fp:
            skipped += 1
            continue
        rows.append((
            fp,
            calculate_md5(fp),
            rec.get("title",  ""),
            rec.get("artist", ""),
            rec.get("album",  ""),
            rec.get("genre",  ""),
            rec.get("year",   None),
        ))

    try:
        with get_db() as cursor:
            cursor.executemany("""
                INSERT OR IGNORE INTO music
                    (file_path, md5_hash, title, artist, album, genre, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
            inserted = cursor.rowcount   # rows actually inserted (IGNORE skips dupes)
            skipped  = len(rows) - inserted
    except Exception as e:
        print(f"[bulk_insert] Error: {e}")

    return inserted, skipped


# ─── Read ─────────────────────────────────────────────────────────────────────
def get_all_songs() -> list[sqlite3.Row]:
    """Return every song in the library, ordered by artist then title."""
    with get_db() as cursor:
        cursor.execute("""
            SELECT id, file_path, title, artist, album, genre, year
            FROM music
            ORDER BY artist COLLATE NOCASE, title COLLATE NOCASE
        """)
        return cursor.fetchall()


def search_by_title(title: str) -> list[sqlite3.Row]:
    """Case-insensitive title search (partial match)."""
    with get_db() as cursor:
        cursor.execute("""
            SELECT file_path, title, artist, album, genre, year
            FROM music
            WHERE title LIKE ?
            ORDER BY title COLLATE NOCASE
        """, (f"%{title}%",))
        return cursor.fetchall()


# kept for backwards compatibility with existing callers
search_for_song = search_by_title


def search_advanced(title: str = "", artist: str = "",
                    genre: str = "") -> list[sqlite3.Row]:
    """
    Filter by any combination of title, artist, and genre.
    Empty strings match everything (wildcard).
    Used by the Advanced Search panel in HarmonyHaven.py.
    """
    with get_db() as cursor:
        cursor.execute("""
            SELECT file_path, title, artist, album, genre, year
            FROM music
            WHERE title  LIKE ?
              AND artist LIKE ?
              AND genre  LIKE ?
            ORDER BY artist COLLATE NOCASE, title COLLATE NOCASE
        """, (f"%{title}%", f"%{artist}%", f"%{genre}%"))
        return cursor.fetchall()


# ─── Update ───────────────────────────────────────────────────────────────────
def update_song_in_db(old_path: str, new_path: str) -> bool:
    """
    Update the file path after a file has been moved/renamed (e.g. by Organize).
    Recalculates the MD5 from the new location.
    Returns True if a row was updated.
    """
    if not os.path.exists(new_path):
        print(f"[update_song_in_db] New path does not exist: {new_path}")
        return False
    new_md5 = calculate_md5(new_path)
    with get_db() as cursor:
        cursor.execute("""
            UPDATE music
            SET file_path = ?, md5_hash = ?
            WHERE file_path = ?
        """, (new_path, new_md5, old_path))
        return cursor.rowcount > 0


def update_metadata(file_path: str, title: str = None, artist: str = None,
                    album: str = None, genre: str = None,
                    year: int = None) -> bool:
    """Update only the metadata columns (leave file_path and md5 alone)."""
    fields, values = [], []
    for col, val in [("title", title), ("artist", artist),
                     ("album", album),  ("genre", genre), ("year", year)]:
        if val is not None:
            fields.append(f"{col} = ?")
            values.append(val)
    if not fields:
        return False
    values.append(file_path)
    with get_db() as cursor:
        cursor.execute(
            f"UPDATE music SET {', '.join(fields)} WHERE file_path = ?", values)
        return cursor.rowcount > 0


# ─── Delete ───────────────────────────────────────────────────────────────────
def delete_song_from_db(file_path: str) -> bool:
    """Remove a song row by file path. Returns True if a row was deleted."""
    with get_db() as cursor:
        cursor.execute("DELETE FROM music WHERE file_path = ?", (file_path,))
        return cursor.rowcount > 0


def delete_missing_files() -> int:
    """
    Scan every row and remove entries whose file no longer exists on disk.
    Returns the number of rows removed.  Useful as a periodic cleanup task.
    """
    with get_db() as cursor:
        cursor.execute("SELECT file_path FROM music")
        all_paths = [row[0] for row in cursor.fetchall()]

    missing = [p for p in all_paths if not os.path.exists(p)]
    if not missing:
        return 0

    with get_db() as cursor:
        cursor.executemany("DELETE FROM music WHERE file_path = ?",
                           [(p,) for p in missing])
        return len(missing)


# ─── Duplicates ───────────────────────────────────────────────────────────────
def find_duplicates() -> list[tuple[str, str]]:
    """
    Return a list of (duplicate_path, original_path) pairs based on MD5 hash.
    The first file seen for a given hash is kept as the 'original'.
    """
    with get_db() as cursor:
        cursor.execute("SELECT file_path, md5_hash FROM music ORDER BY id")
        rows = cursor.fetchall()

    seen, duplicates = {}, []
    for row in rows:
        fp, h = row["file_path"], row["md5_hash"]
        if h in seen:
            duplicates.append((fp, seen[h]))
        else:
            seen[h] = fp
    return duplicates


# ─── Stats ────────────────────────────────────────────────────────────────────
def get_library_stats() -> dict:
    """Return a summary dict — handy for a future dashboard / status bar."""
    with get_db() as cursor:
        cursor.execute("SELECT COUNT(*) FROM music")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT artist) FROM music WHERE artist != ''")
        artists = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT album) FROM music WHERE album != ''")
        albums = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT genre) FROM music WHERE genre != ''")
        genres = cursor.fetchone()[0]

    return {"total_tracks": total, "artists": artists,
            "albums": albums, "genres": genres}


# ─── Init ─────────────────────────────────────────────────────────────────────
create_music_table()

# Created by Alejandro X. Solis Owner of TechFusion Repairs LLC
# MIT License
# All Rights Reserved.
# See LICENSE file for more details.
# © 2024 TechFusion Repairs LLC. All rights reserved.