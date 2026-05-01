from app.database import get_db


def get_events_for_car(car_id):
    conn = get_db()
    events = conn.execute(
        'SELECT * FROM events WHERE car_id=? ORDER BY date DESC', (car_id,)
    ).fetchall()
    conn.close()
    return events


def get_event_by_id(event_id):
    conn = get_db()
    event = conn.execute('SELECT * FROM events WHERE id=?', (event_id,)).fetchone()
    conn.close()
    return event


def add_event(car_id, date, mileage, description, photo):
    conn = get_db()
    conn.execute(
        'INSERT INTO events (car_id, date, mileage, description, photo) VALUES (?, ?, ?, ?, ?)',
        (car_id, date, mileage, description, photo),
    )
    conn.commit()
    conn.close()


def update_event(event_id, date, mileage, description, photo):
    conn = get_db()
    conn.execute(
        'UPDATE events SET date=?, mileage=?, description=?, photo=? WHERE id=?',
        (date, mileage, description, photo, event_id),
    )
    conn.commit()
    conn.close()


def delete_event_by_id(event_id):
    conn = get_db()
    conn.execute('DELETE FROM events WHERE id=?', (event_id,))
    conn.commit()
    conn.close()
