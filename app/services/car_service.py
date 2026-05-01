from app.database import get_db, get_vehicles_db


def get_all_cars():
    conn = get_db()
    cars = conn.execute('SELECT * FROM cars').fetchall()
    conn.close()
    return cars


def get_all_vehicles():
    conn = get_vehicles_db()
    vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    conn.close()
    return vehicles


def get_vehicle_by_id(vehicle_id):
    conn = get_vehicles_db()
    vehicle = conn.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,)).fetchone()
    conn.close()
    return vehicle


def create_car(custom_name, vehicle):
    conn = get_db()
    conn.execute(
        '''INSERT INTO cars
           (custom_name, make, model, oil_service_interval, inspection_interval)
           VALUES (?, ?, ?, ?, ?)''',
        (custom_name, vehicle['make'], vehicle['model'],
         vehicle['oil_service_interval'], vehicle['inspection_interval']),
    )
    conn.commit()
    conn.close()


def get_car_by_id(car_id):
    conn = get_db()
    car = conn.execute('SELECT * FROM cars WHERE id=?', (car_id,)).fetchone()
    conn.close()
    return car


def delete_car_by_id(car_id):
    conn = get_db()
    conn.execute('DELETE FROM events WHERE car_id=?', (car_id,))
    conn.execute('DELETE FROM cars WHERE id=?', (car_id,))
    conn.commit()
    conn.close()
