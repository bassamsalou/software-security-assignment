import sqlite3
from pathlib import Path

DATABASE_path = Path(__file__).parent / "bookings.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_path)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            owner TEXT NOT NULL,
            destination TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            owner TEXT NOT NULL,
            summary TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM bookings")

    if cursor.fetchone()[0] == 0:
        bookings = [
            (1, "John", "Copenhagen", "2026-11-10", "confirmed"),
            (2, "John", "Berlin", "2026-12-05", "confirmed"),
            (3, "Doe", "Amsterdam", "2026-11-20", "confirmed"),
            (4, "Doe", "Paris", "2027-01-15", "pending"),
        ]

        cursor.executemany('''
            INSERT INTO bookings (id, owner, destination, booking_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', bookings)
 
    connection.commit()
    connection.close()