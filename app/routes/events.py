import os
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from app.services.event_service import (
    get_events_for_car,
    add_event,
    get_event_by_id,
    update_event,
    delete_event_by_id,
)
from app.services.maintenance_service import compute_due_list, MAINTENANCE_TASKS

events_bp = Blueprint('events', __name__)


@events_bp.route('/car/<int:car_id>')
def index(car_id):
    session['car_id'] = car_id
    events = get_events_for_car(car_id)
    return render_template('index.html', events=events)


@events_bp.route('/add', methods=['POST'])
def add():
    car_id = session.get('car_id')
    date = request.form['date']
    mileage = int(request.form['mileage'].replace('.', ''))
    original_description = request.form['description'].strip()

    tasks = [t.lower() for t in request.form.getlist('tasks')]
    if original_description:
        tasks.append(original_description)
    full_description = ', '.join(tasks)

    filename = _save_photo(request.files.get('photo'))
    add_event(car_id, date, mileage, full_description, filename)
    return redirect(url_for('events.index', car_id=car_id))


@events_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    car_id = session.get('car_id')
    event = get_event_by_id(id)
    if not event:
        return "Event not found!", 404

    if request.method == 'POST':
        date = request.form['date']
        mileage = int(request.form['mileage'].replace('.', ''))
        selected_tasks = request.form.getlist('tasks')
        manual_note = request.form['manual_note'].strip()
        new_description = ', '.join(selected_tasks + ([manual_note] if manual_note else []))

        filename = event['photo']
        new_photo = request.files.get('photo')
        if new_photo and new_photo.filename:
            if filename:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                except OSError:
                    pass
            filename = _save_photo(new_photo)

        update_event(id, date, mileage, new_description, filename)
        return redirect(url_for('events.index', car_id=car_id))

    # GET: parse existing description back into tasks + manual note
    parts = [p.strip() for p in event['description'].split(',') if p.strip()]
    task_names = [t for t in MAINTENANCE_TASKS]
    selected_tasks, manual_parts = [], []
    for part in parts:
        matched = next((t for t in task_names if part.lower() == t.lower()), None)
        if matched:
            selected_tasks.append(matched)
        else:
            manual_parts.append(part)
    manual_note = ', '.join(manual_parts)
    return render_template('edit.html', event=event, selected_tasks=selected_tasks, manual_note=manual_note)


@events_bp.route('/delete/<int:id>')
def delete(id):
    car_id = session.get('car_id')
    event = get_event_by_id(id)
    if event and event['photo']:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], event['photo']))
        except OSError:
            pass
    delete_event_by_id(id)
    return redirect(url_for('events.index', car_id=car_id))


@events_bp.route('/upcoming')
def upcoming():
    car_id = session.get('car_id')
    due_list, car = compute_due_list(car_id)
    if car is None:
        return "Car not found!", 404
    return render_template('upcoming.html', due_list=due_list, car=car)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _save_photo(photo):
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None
