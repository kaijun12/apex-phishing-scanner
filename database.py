import sqlite3
from datetime import datetime

DB_PATH = 'scans.db'


def init_db():
    """Create the scans table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            analysis TEXT,
            audio_filename TEXT,
            scanned_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def save_scan(filename, extracted_text, analysis, audio_filename):
    """Save a completed scan to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO scans (filename, extracted_text, analysis, audio_filename, scanned_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, extracted_text, analysis, audio_filename, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_all_scans():
    """Retrieve all past scans, newest first."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM scans ORDER BY scanned_at DESC')
    rows = cursor.fetchall()

    conn.close()
    return rows