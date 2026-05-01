import os
from pathlib import Path

_BASE = Path(__file__).parent.parent  # project root
_INSTANCE = _BASE / 'instance'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-before-production')
    DATABASE = str(_INSTANCE / 'database.db')
    VEHICLES_DATABASE = str(_INSTANCE / 'vehicles.db')
    UPLOAD_FOLDER = str(_BASE / 'static' / 'uploads')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
