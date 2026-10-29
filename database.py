import sqlite3
from pathlib import Path


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "database.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(DB_NAME)

    # Allows us to access columns by name
    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    db = get_db()


    # =====================================================
    # USERS TABLE
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'user',

            full_name TEXT DEFAULT '',

            email TEXT DEFAULT ''

        )
    """)


    # =====================================================
    # REPORTS TABLE
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS reports (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,

            scam_type TEXT,

            incident_date TEXT,

            description TEXT,

            contact TEXT,

            financial_loss TEXT,

            evidence TEXT,

            notes TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TEXT

        )
    """)


    # =====================================================
    # FEEDBACK TABLE
    # =====================================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS feedback (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            email TEXT,

            message TEXT,

            rating INTEGER,

            created_at TEXT

        )
    """)


    # =====================================================
    # DEFAULT ADMIN ACCOUNT
    # =====================================================

    db.execute("""
        INSERT OR IGNORE INTO users
        (
            username,
            password,
            role,
            full_name,
            email
        )

        VALUES
        (
            'admin',
            'admin123',
            'admin',
            'Administrator',
            'admin@example.com'
        )
    """)


    # =====================================================
    # DEFAULT DEMO USER
    # =====================================================

    db.execute("""
        INSERT OR IGNORE INTO users
        (
            username,
            password,
            role,
            full_name,
            email
        )

        VALUES
        (
            'user',
            'user123',
            'user',
            'Demo User',
            'user@example.com'
        )
    """)


    # =====================================================
    # SAVE CHANGES
    # =====================================================

    db.commit()

    db.close()


# =========================================================
# RUN DATABASE INITIALIZATION DIRECTLY
# =========================================================

if __name__ == "__main__":

    init_db()

    print("Database initialized successfully!")
    print(f"Database location: {DB_NAME}")