import sqlite3
from flask import current_app


def get_db():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_vehicles_db():
    conn = sqlite3.connect(current_app.config['VEHICLES_DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn
