import os
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

# Ensure Gunicorn can find 'app'
app = create_app()  # ✅ Add this

if __name__ == "__main__":
    # ✅ Explicitly bind Flask to Heroku's assigned port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
