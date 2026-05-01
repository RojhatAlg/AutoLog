from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.car_service import (
    get_all_cars,
    get_all_vehicles,
    get_vehicle_by_id,
    create_car,
    delete_car_by_id,
)

cars_bp = Blueprint('cars', __name__)


@cars_bp.route('/')
def start():
    cars = get_all_cars()
    vehicles = get_all_vehicles()
    return render_template('start.html', cars=cars, vehicles=vehicles)


@cars_bp.route('/new_car', methods=['POST'])
def new_car():
    vehicle_id = request.form['vehicle_id']
    custom_name = request.form['custom_name']
    vehicle = get_vehicle_by_id(vehicle_id)
    create_car(custom_name, vehicle)
    return redirect(url_for('cars.start'))


@cars_bp.route('/select_car', methods=['POST'])
def select_car():
    car_id = request.form['car_id']
    session['car_id'] = car_id
    return redirect(url_for('events.index', car_id=car_id))


@cars_bp.route('/delete_car/<int:car_id>')
def delete_car(car_id):
    delete_car_by_id(car_id)
    return redirect(url_for('cars.start'))
