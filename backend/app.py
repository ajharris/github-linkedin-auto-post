import os
from flask import Flask
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes
from backend.config import config_dict

def create_app(config_name=None):
    """Flask application factory function."""
    config_name = config_name or os.getenv("FLASK_CONFIG", "production")
    app = Flask(__name__)

    config_obj = config_dict.get(config_name)
    if config_obj is None:
        raise ValueError(f"Invalid config name: {config_name}")

    app.config.from_object(config_obj)

    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(routes)

    return app

# ✅ Use this as the entry point for Gunicorn
app = create_app()
