from flask import Flask
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes
from backend.config import config_dict
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "default")
    """Flask application factory function."""
    app = Flask(__name__)

    config_obj = config_dict.get(config_name or "default")
    app.config.from_object(config_obj)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(routes)

    return app
