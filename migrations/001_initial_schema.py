"""Migration 001 — Create cars and events tables."""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).parent.parent / 'instance' / 'database.db'


def run():
    conn = sqlite3.connect(DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            custom_name TEXT,
            make TEXT,
            model TEXT,
            oil_service_interval INTEGER,
            inspection_interval INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            date TEXT,
            mileage INTEGER,
            description TEXT,
            photo TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("001: cars and events tables ready.")


if __name__ == '__main__':
    run()
