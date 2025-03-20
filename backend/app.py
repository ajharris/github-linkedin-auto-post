from flask import Flask
from flask_migrate import Migrate
from backend.models import db
from backend.routes import routes  # Import routes blueprint
import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Get absolute path of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicitly set the frontend build path
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend/build")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.config.from_object("backend.config.Config")

db.init_app(app)

migrate = Migrate(app, db)

# ✅ Register the blueprint **without a prefix** (ensure it's at `/webhook/github`)
app.register_blueprint(routes)  # ✅ Ensure it is correctly registered

if __name__ == "__main__":
    app.run(port=5000, debug=True)
