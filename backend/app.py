# backend/app.py

import os
from flask import Flask, send_from_directory
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes
from backend.config import config
from dotenv import load_dotenv

import logging

load_dotenv()

def create_app(config_name=None):
    """Flask application factory function."""
    config_name = config_name or os.getenv("FLASK_CONFIG", "production")
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="")
    app.logger.setLevel(logging.INFO)

    app.logger.info(f"[App] Starting application with config: {config_name}")

    config_obj = config.get(config_name)
    if config_obj is None:
        app.logger.error(f"[App] Invalid config name: {config_name}")
        raise ValueError(f"Invalid config name: {config_name}")

    app.config.from_object(config_obj)
    app.logger.info("[App] Configuration loaded successfully.")

    # Validate required environment variables
    required_env_vars = ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_USER_ID"]
    missing_vars = [
        var for var in required_env_vars
        if not os.getenv(var) and not (var == "LINKEDIN_USER_ID" and os.getenv("SEED_LINKEDIN_ID"))
    ]
    if missing_vars:
        app.logger.error(f"[App] Missing required environment variables: {missing_vars}")
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")

    app.register_blueprint(routes)

    db.init_app(app)
    Migrate(app, db)

    # Serve React frontend
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        file_path = os.path.normpath(os.path.join(app.static_folder, path))

        if file_path.startswith(app.static_folder) and os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")
        
    # 🔽 CLI command
    @app.cli.command("seed-user")
    def seed_user():
        from backend.scripts.seed_main_user import seed_main_user
        seed_main_user(app)

    return app
