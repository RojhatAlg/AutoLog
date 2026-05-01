import sqlite3

conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(vehicles)")
columns = cursor.fetchall()

print("Current Vehicles Table Columns:")
for col in columns:
    print(col)

conn.close()
