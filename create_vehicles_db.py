import sqlite3

conn = sqlite3.connect('vehicles.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT,
    model TEXT,
    oil_service_interval INTEGER,
    inspection_interval INTEGER
)
''')

vehicles = [
    ('Volkswagen', 'Tiguan', 15000, 30000),
    ('BMW', 'F10 525d', 20000, 40000),
    ('Toyota', 'RAV4', 15000, 30000),
    ('Tesla', 'Model S', 25000, 40000)
]

c.executemany('''
INSERT INTO vehicles (make, model, oil_service_interval, inspection_interval)
VALUES (?, ?, ?, ?)
''', vehicles)

conn.commit()
conn.close()

print("vehicles.db created and populated successfully!")
