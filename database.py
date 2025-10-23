# database.py
import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "mydatabase.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

    # Optional: Create a default user if not exists
    user = conn.execute("SELECT * FROM users WHERE username = ?", ("admin",)).fetchone()
    if not user:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123"))
        )
        conn.commit()

    conn.close()
