"""Migration 003 — Add brake_disc_front_interval and brake_disc_rear_interval to cars."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / 'instance' / 'database.db'

COLUMNS = ['brake_disc_front_interval', 'brake_disc_rear_interval']


def run():
    conn = sqlite3.connect(DB)
    existing = [row[1] for row in conn.execute('PRAGMA table_info(cars)').fetchall()]
    for col in COLUMNS:
        if col not in existing:
            conn.execute(f'ALTER TABLE cars ADD COLUMN {col} INTEGER')
            print(f"003: added column {col}")
        else:
            print(f"003: {col} already exists, skipping")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    run()
