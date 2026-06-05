import sqlite3
import os
from datetime import date

DB_PATH = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            is_premium  INTEGER DEFAULT 0,
            premium_until TEXT,
            joined_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            action      TEXT,
            used_at     TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def is_premium(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT is_premium, premium_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    if row[0] == 1:
        if row[1] and row[1] >= str(date.today()):
            return True
    return False

def get_today_usage(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = str(date.today())
    c.execute("""
        SELECT COUNT(*) FROM usage
        WHERE user_id = ? AND used_at LIKE ?
    """, (user_id, f"{today}%"))
    count = c.fetchone()[0]
    conn.close()
    return count

def log_usage(user_id: int, action: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO usage (user_id, action) VALUES (?, ?)", (user_id, action))
    conn.commit()
    conn.close()

def activate_premium(user_id: int, days: int = 30):
    from datetime import timedelta
    until = str(date.today() + timedelta(days=days))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?", (until, user_id))
    conn.commit()
    conn.close()
