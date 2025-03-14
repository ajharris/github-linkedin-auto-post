from flask import Flask
from dotenv import load_dotenv
from config import Config
from extensions import db
from routes import register_blueprints

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

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
