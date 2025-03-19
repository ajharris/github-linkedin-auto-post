from flask import Flask
from flask_migrate import Migrate
from models import db
from routes import routes  # Import routes blueprint
import os

from dotenv import load_dotenv

load_dotenv()

# Get absolute path of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicitly set the frontend build path
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend/build")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.config.from_object("config")
db.init_app(app)

migrate = Migrate(app, db)

# Register the blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
