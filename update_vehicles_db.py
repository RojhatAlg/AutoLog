import sqlite3

conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()

# Drop old table and recreate with correct columns
cursor.execute('DROP TABLE IF EXISTS vehicles')

cursor.execute('''
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT,
    model TEXT,
    oil_service_interval INTEGER,
    inspection_interval INTEGER,
    diesel_filter_interval INTEGER,
    brake_pads_front_interval INTEGER,
    brake_pads_rear_interval INTEGER,
    micro_filter_interval INTEGER,
    coupe_filter_interval INTEGER,
    air_filter_interval INTEGER,
    glow_plugs_interval INTEGER,
    brake_fluid_interval INTEGER,
    vehicle_inspection_interval INTEGER,
    eu_control_interval INTEGER,
    brake_disc_front_interval INTEGER,
    brake_disc_rear_interval INTEGER
)
''')

# Vehicles with **exactly 14 values** after `NULL`
vehicles = [
    ('BMW', 'F10 525d', 10000, 40000, 40000, 40000, 40000, 30000, 20000, 60000, 80000, 40000, 60000, 60000, 60000, 90000),
    ('Volkswagen', 'Tiguan', 15000, 30000, 30000, 30000, 30000, 25000, 15000, 50000, 70000, 30000, 50000, 50000, 60000, 90000)
]

cursor.executemany('''
INSERT INTO vehicles (
    make, model, oil_service_interval, inspection_interval, diesel_filter_interval,
    brake_pads_front_interval, brake_pads_rear_interval, micro_filter_interval, coupe_filter_interval,
    air_filter_interval, glow_plugs_interval, brake_fluid_interval, vehicle_inspection_interval, eu_control_interval, brake_disc_front_interval, brake_disc_rear_interval
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', vehicles)

conn.commit()
conn.close()

print("vehicles.db updated successfully!")
