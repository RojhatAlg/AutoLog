import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(cars)")
columns = [column[1] for column in cursor.fetchall()]
print("Current columns in cars table:", columns)

# Add brake_disc_front_interval column if it doesn't exist
if 'brake_disc_front_interval' not in columns:
    cursor.execute('ALTER TABLE cars ADD COLUMN brake_disc_front_interval INTEGER')
    print("Added brake_disc_front_interval column")
else:
    print("brake_disc_front_interval column already exists")

# Add brake_disc_rear_interval column if it doesn't exist
if 'brake_disc_rear_interval' not in columns:
    cursor.execute('ALTER TABLE cars ADD COLUMN brake_disc_rear_interval INTEGER')
    print("Added brake_disc_rear_interval column")
else:
    print("brake_disc_rear_interval column already exists")

conn.commit()
conn.close()

print("\ndatabase.db updated successfully!")
print("The brake disc intervals will now be fetched from vehicles.db defaults.")
