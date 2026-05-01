"""
Seed script — populates vehicles.db with the reference catalog.
Run once: python scripts/seed_vehicles.py
WARNING: drops and recreates the vehicles table each run.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / 'instance' / 'vehicles.db'


SCHEMA = '''
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
'''

# (make, model, oil, inspection, diesel_filter, bp_front, bp_rear,
#  micro, coupe, air, glow, brake_fluid, veh_insp, eu_ctrl, bd_front, bd_rear)
VEHICLES = [
    ('BMW',        'F10 525d', 10000, 40000, 40000, 40000, 40000, 30000, 20000, 60000, 80000, 40000, 60000, 60000, 60000, 90000),
    ('Volkswagen', 'Tiguan',   15000, 30000, 30000, 30000, 30000, 25000, 15000, 50000, 70000, 30000, 50000, 50000, 60000, 90000),
]

INSERT = '''
    INSERT INTO vehicles (
        make, model, oil_service_interval, inspection_interval,
        diesel_filter_interval, brake_pads_front_interval, brake_pads_rear_interval,
        micro_filter_interval, coupe_filter_interval, air_filter_interval,
        glow_plugs_interval, brake_fluid_interval, vehicle_inspection_interval,
        eu_control_interval, brake_disc_front_interval, brake_disc_rear_interval
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''


def run():
    conn = sqlite3.connect(DB)
    conn.execute('DROP TABLE IF EXISTS vehicles')
    conn.execute(SCHEMA)
    conn.executemany(INSERT, VEHICLES)
    conn.commit()
    conn.close()
    print(f"vehicles.db seeded with {len(VEHICLES)} vehicles.")


if __name__ == '__main__':
    run()
