from datetime import datetime
from app.database import get_db, get_vehicles_db
from app.services.car_service import get_car_by_id
from app.utils import add_years

# Canonical task name → (interval column key, unit)
MAINTENANCE_TASKS = {
    "Oil service":          ("oil_service_interval",         "km"),
    "Diesel filter":        ("diesel_filter_interval",       "km"),
    "Brake pads front":     ("brake_pads_front_interval",    "km"),
    "Brake pads rear":      ("brake_pads_rear_interval",     "km"),
    "Brake disc front":     ("brake_disc_front_interval",    "km"),
    "Brake disc rear":      ("brake_disc_rear_interval",     "km"),
    "Brake fluid":          ("brake_fluid_interval",         "years"),
    "Micro filter":         ("micro_filter_interval",        "km"),
    "Coupe filter":         ("coupe_filter_interval",        "km"),
    "Air filter":           ("air_filter_interval",          "km"),
    "Glow plugs":           ("glow_plugs_interval",          "km"),
    "Vehicle inspection":   ("vehicle_inspection_interval",  "km"),
    "EU control":           ("eu_control_interval",          "years"),
}


def compute_due_list(car_id):
    car = get_car_by_id(car_id)
    if not car:
        return [], None
    car_dict = dict(car)

    # Look up vehicle defaults from catalog
    conn_v = get_vehicles_db()
    vehicle = conn_v.execute(
        'SELECT * FROM vehicles WHERE make=? AND model=?',
        (car_dict['make'], car_dict['model']),
    ).fetchone()
    defaults = dict(vehicle) if vehicle else {}
    conn_v.close()

    conn = get_db()
    events = conn.execute(
        'SELECT mileage, date, description FROM events WHERE car_id=? ORDER BY mileage DESC',
        (car_id,),
    ).fetchall()
    conn.close()

    due_list = []
    for task, (col, unit) in MAINTENANCE_TASKS.items():
        interval = car_dict.get(col) or defaults.get(col) or 0
        if not interval:
            continue

        task_lower = task.lower()

        if unit == "km":
            last_mileage = _last_mileage_for_task(events, task_lower)
            if last_mileage is not None:
                due_list.append(f"{task} due at {last_mileage + interval:,} km")
            else:
                due_list.append(f"{task} first due at {interval:,} km")

        elif unit == "years":
            if interval > 10:
                interval = 2
            last_date = _last_date_for_task(events, task_lower)
            if last_date is not None:
                next_due = add_years(last_date, interval)
                due_list.append(f"{task} due on {next_due.strftime('%Y-%m-%d')}")
            else:
                next_due = add_years(datetime.today(), interval)
                due_list.append(f"{task} first due on {next_due.strftime('%Y-%m-%d')}")

    return due_list, car_dict


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _last_mileage_for_task(events, task_lower):
    last = None
    for ev in events:
        parts = [p.strip().lower() for p in ev['description'].split(',') if p.strip()]
        if task_lower in parts:
            if last is None or ev['mileage'] > last:
                last = ev['mileage']
    return last


def _last_date_for_task(events, task_lower):
    last = None
    for ev in events:
        parts = [p.strip().lower() for p in ev['description'].split(',') if p.strip()]
        if task_lower in parts:
            try:
                ev_date = datetime.strptime(ev['date'], "%Y-%m-%d")
                if last is None or ev_date > last:
                    last = ev_date
            except ValueError:
                continue
    return last
