# backend/app.py

import os
from flask import Flask, send_from_directory
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes
from backend.config import config_dict

import logging


def create_app(config_name=None):
    """Flask application factory function."""
    config_name = config_name or os.getenv("FLASK_CONFIG", "production")
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="")

    config_obj = config_dict.get(config_name)
    if config_obj is None:
        raise ValueError(f"Invalid config name: {config_name}")

    app.config.from_object(config_obj)
    app.register_blueprint(routes)

    db.init_app(app)
    Migrate(app, db)

    # Serve React frontend
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        file_path = os.path.join(app.static_folder, path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")

    return app
