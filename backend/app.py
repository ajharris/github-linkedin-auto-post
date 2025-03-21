from flask import Flask
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes  # Import routes blueprint
from backend.config import config_dict  # Import config dictionary

def create_app(config_name="default"):
    """Flask application factory function."""
    app = Flask(__name__)

    # Load configuration dynamically
    app.config.from_object(config_dict[config_name])

    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(routes)

    return app

# ✅ Only run the app if executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)
