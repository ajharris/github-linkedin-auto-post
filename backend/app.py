from flask import Flask
from dotenv import load_dotenv
from backend.config import Config
from backend.extensions import db
from backend.routes import register_blueprints

# Load environment variables
load_dotenv()

# Create Flask app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register routes
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

# Explicitly expose the app for Gunicorn
app = create_app()  # Ensure this is outside the main block

if __name__ == "__main__":
    app.run(debug=True)
