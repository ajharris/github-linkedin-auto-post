import os
from flask import Flask
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes
from backend.config import config_dict

app = Flask(__name__)

app.register_blueprint(routes)

def create_app(config_name=None):
    """Flask application factory function."""

    # Default to 'production' if not explicitly set
    config_name = config_name or os.getenv("FLASK_CONFIG", "production")

    app = Flask(__name__)

    # Load the configuration object from config_dict
    config_obj = config_dict.get(config_name)
    if config_obj is None:
        raise ValueError(f"Invalid config name: {config_name}")

    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register routes
    app.register_blueprint(routes)

    return app
