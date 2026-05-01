import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check existing columns first
cursor.execute("PRAGMA table_info(cars)")
existing_columns = [column[1] for column in cursor.fetchall()]

if 'oil_service_interval' not in existing_columns:
    cursor.execute('ALTER TABLE cars ADD COLUMN oil_service_interval INTEGER')

if 'inspection_interval' not in existing_columns:
    cursor.execute('ALTER TABLE cars ADD COLUMN inspection_interval INTEGER')

conn.commit()
conn.close()

print("Columns checked and updated successfully!")
