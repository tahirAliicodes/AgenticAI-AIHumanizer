import sqlite3
from datetime import datetime

DB_FILE = "history.db"  # this is the actual file that gets created on your disk


def init_db():
    """
    Run this ONCE when the app starts.
    It creates the 'jobs' table if it doesn't already exist.
    Think of this as setting up the blank Excel sheet with column headers.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_job(filename: str, word_count: int, status: str = "success"):
    """
    Call this every time a humanize job finishes.
    It adds ONE new row to the table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (filename, word_count, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (filename, word_count, status, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_all_jobs():
    """
    Returns every row in the table, newest first.
    This is what the dashboard will call to show history.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_stats():
    """
    Returns summary numbers for the dashboard:
    total jobs run, and total words humanized.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(word_count) FROM jobs WHERE status = 'success'")
    total_jobs, total_words = cursor.fetchone()
    conn.close()
    return {
        "total_jobs": total_jobs or 0,
        "total_words": total_words or 0
    }
if __name__ == "__main__":
    init_db()
    print("Database created! Check your folder for history.db")