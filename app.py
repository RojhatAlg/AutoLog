from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os
from werkzeug.utils import secure_filename

from datetime import datetime

def add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=d.day-1)



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            custom_name TEXT,
            make TEXT,
            model TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            date TEXT,
            mileage INTEGER,
            description TEXT,
            photo TEXT
        )
    ''')
    conn.close()

# Start page: select or create car
@app.route('/')
def start():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cars = conn.execute('SELECT * FROM cars').fetchall()
    conn.close()

    conn2 = sqlite3.connect('vehicles.db')
    conn2.row_factory = sqlite3.Row
    vehicles = conn2.execute('SELECT * FROM vehicles').fetchall()
    conn2.close()

    return render_template('start.html', cars=cars, vehicles=vehicles)

# Handle new car creation
@app.route('/new_car', methods=['POST'])
def new_car():
    vehicle_id = request.form['vehicle_id']
    custom_name = request.form['custom_name']

    conn2 = sqlite3.connect('vehicles.db')
    conn2.row_factory = sqlite3.Row
    vehicle = conn2.execute('SELECT * FROM vehicles WHERE id=?', (vehicle_id,)).fetchone()
    conn2.close()

    conn = sqlite3.connect('database.db')
    conn.execute('''
        INSERT INTO cars (custom_name, make, model, oil_service_interval, inspection_interval)
        VALUES (?, ?, ?, ?, ?)
    ''', (custom_name, vehicle['make'], vehicle['model'],
          vehicle['oil_service_interval'], vehicle['inspection_interval']))
    conn.commit()
    conn.close()

    return redirect(url_for('start'))


# Select car to view events
@app.route('/select_car', methods=['POST'])
def select_car():
    car_id = request.form['car_id']
    session['car_id'] = car_id
    return redirect(url_for('index', car_id=car_id))

# Car diary (events)
@app.route('/car/<int:car_id>')
def index(car_id):
    session['car_id'] = car_id
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    events = conn.execute('SELECT * FROM events WHERE car_id=? ORDER BY date DESC', (car_id,)).fetchall()
    conn.close()
    return render_template('index.html', events=events)


@app.route('/add', methods=['POST'])
def add():
    car_id = session.get('car_id')
    date = request.form['date']
    mileage = int(request.form['mileage'].replace('.', ''))
    original_description = request.form['description'].strip()

    tasks = request.form.getlist('tasks') 
    task_descriptions = tasks.copy()  

    task_descriptions = [task.lower() for task in task_descriptions]

    if original_description:
        task_descriptions.append(original_description)

    full_description = ', '.join(task_descriptions)

    # Handle file upload
    photo = request.files['photo']
    filename = secure_filename(photo.filename) if photo and photo.filename else None
    if filename:
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Store in database
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO events (car_id, date, mileage, description, photo) VALUES (?, ?, ?, ?, ?)',
                 (car_id, date, mileage, full_description, filename))
    conn.commit()
    conn.close()

    return redirect(url_for('index', car_id=car_id))



# Delete event
@app.route('/delete/<int:id>')
def delete(id):
    car_id = session.get('car_id')
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    event = conn.execute('SELECT photo FROM events WHERE id=?', (id,)).fetchone()
    if event['photo']:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], event['photo']))
        except:
            pass
    conn.execute('DELETE FROM events WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', car_id=car_id))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    car_id = session.get('car_id')
    # Define the canonical list of maintenance tasks:
    maintenance_tasks = [
        "Oil service", "Diesel filter", "Brake pads front", "Brake pads rear",
        "Brake disc front", "Brake disc rear", "Brake fluid", "Micro filter",
        "Coupe filter", "Air filter", "Glow plugs", "Vehicle inspection", "EU control"
    ]
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    event = conn.execute('SELECT * FROM events WHERE id=?', (id,)).fetchone()
    if not event:
        conn.close()
        return "Event not found!", 404

    if request.method == 'POST':
        date = request.form['date']
        mileage = int(request.form['mileage'].replace('.', ''))
        selected_tasks = request.form.getlist('tasks') 
        manual_note = request.form['manual_note'].strip()

        new_description = ', '.join(selected_tasks + ([manual_note] if manual_note else []))
        
        photo = request.files['photo']
        filename = event['photo']
        if photo and photo.filename:
            if filename:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        conn.execute('UPDATE events SET date=?, mileage=?, description=?, photo=? WHERE id=?',
                     (date, mileage, new_description, filename, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index', car_id=car_id))
    else:
        parts = [p.strip() for p in event['description'].split(',') if p.strip()]
        selected_tasks = []
        manual_parts = []
        for part in parts:
            matched = False
            for task in maintenance_tasks:
                if part.lower() == task.lower():
                    selected_tasks.append(task)
                    matched = True
                    break
            if not matched:
                manual_parts.append(part)
        manual_note = ', '.join(manual_parts)
        conn.close()
        return render_template('edit.html', event=event, selected_tasks=selected_tasks, manual_note=manual_note)


@app.route('/upcoming')
def upcoming():
    car_id = session.get('car_id')
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    car = conn.execute('SELECT * FROM cars WHERE id=?', (car_id,)).fetchone()
    if not car:
        conn.close()
        return "Car not found!", 404
    car_dict = dict(car)

    defaults = {}
    conn2 = sqlite3.connect('vehicles.db')
    conn2.row_factory = sqlite3.Row
    vehicle = conn2.execute('SELECT * FROM vehicles WHERE make=? AND model=?', 
                            (car_dict['make'], car_dict['model'])).fetchone()
    if vehicle:
        defaults = dict(vehicle)
    conn2.close()
    

    def get_interval(key):
        val = car_dict.get(key, 0) or defaults.get(key, 0)
        return val

    maintenance_tasks = {
        "oil service": (get_interval('oil_service_interval'), "km"),
        "diesel filter": (get_interval('diesel_filter_interval'), "km"),
        "brake pads front": (get_interval('brake_pads_front_interval'), "km"),
        "brake pads rear": (get_interval('brake_pads_rear_interval'), "km"),
        "brake disc front": (get_interval('brake_disc_front_interval'), "km"),
        "brake disc rear": (get_interval('brake_disc_rear_interval'), "km"),
        "brake fluid": (get_interval('brake_fluid_interval'), "years"),
        "micro filter": (get_interval('micro_filter_interval'), "km"),
        "coupe filter": (get_interval('coupe_filter_interval'), "km"),
        "air filter": (get_interval('air_filter_interval'), "km"),
        "glow plugs": (get_interval('glow_plugs_interval'), "km"),
        "vehicle inspection": (get_interval('vehicle_inspection_interval'), "km"),
        "eu control": (get_interval('eu_control_interval'), "years")
    }
    
    due_list = []
    events = conn.execute('SELECT mileage, date, description FROM events WHERE car_id=? ORDER BY mileage DESC', (car_id,)).fetchall()
    
    for task, (interval, typ) in maintenance_tasks.items():
        if interval:
            if typ == "km":
                last_mileage = None
                for ev in events:
                    parts = [p.strip().lower() for p in ev['description'].split(',') if p.strip()]
                    if task in parts:
                        if last_mileage is None or ev['mileage'] > last_mileage:
                            last_mileage = ev['mileage']
                if last_mileage is not None:
                    next_due = last_mileage + interval
                    due_list.append(f"{task.capitalize()} due at {next_due:,} km")
                else:
                    due_list.append(f"{task.capitalize()} first due at {interval:,} km")
            elif typ == "years":
                if interval > 10:
                    interval = 2
                last_date = None
                for ev in events:
                    parts = [p.strip().lower() for p in ev['description'].split(',') if p.strip()]
                    if task in parts:
                        try:
                            ev_date = datetime.strptime(ev['date'], "%Y-%m-%d")
                            if last_date is None or ev_date > last_date:
                                last_date = ev_date
                        except Exception as e:
                            continue
                if last_date is not None:
                    next_due_date = add_years(last_date, interval)
                    due_list.append(f"{task.capitalize()} due on {next_due_date.strftime('%Y-%m-%d')}")
                else:
                    today = datetime.today()
                    next_due_date = add_years(today, interval)
                    due_list.append(f"{task.capitalize()} first due on {next_due_date.strftime('%Y-%m-%d')}")
    conn.close()
    
    return render_template('upcoming.html', due_list=due_list, car=car_dict)










@app.route('/delete_car/<int:car_id>', methods=['GET'])
def delete_car(car_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Delete associated events first
    cursor.execute('DELETE FROM events WHERE car_id=?', (car_id,))

    # Then delete the car
    cursor.execute('DELETE FROM cars WHERE id=?', (car_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('start'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
