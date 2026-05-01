import os
from flask import Flask
from app.config import DevelopmentConfig


def create_app(config=DevelopmentConfig):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
        instance_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance'),
        instance_relative_config=False,
    )
    app.config.from_object(config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from app.routes.cars import cars_bp
    from app.routes.events import events_bp
    app.register_blueprint(cars_bp)
    app.register_blueprint(events_bp)

    return app
