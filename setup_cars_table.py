import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    custom_name TEXT,
    make TEXT,
    model TEXT,
    oil_service_interval INTEGER,
    inspection_interval INTEGER
)
''')

conn.commit()
conn.close()
