import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import local modules
try:
    from auth import linkedin_oauth
    from github_webhook import handle_github_event
    from database_service import create_client_database
    from models import db
except ImportError as e:
    print(f"Warning: Missing module - {e}")

app = Flask(__name__)

# Fix Heroku's `postgres://` issue for compatibility with SQLAlchemy
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///local.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register LinkedIn OAuth if available
if 'linkedin_oauth' in globals():
    app.register_blueprint(linkedin_oauth, url_prefix="/auth")

# GitHub Webhook Route
@app.route('/webhook/github', methods=['POST'])
def webhook():
    if 'handle_github_event' in globals():
        return handle_github_event()
    return jsonify({"error": "GitHub webhook handler not implemented"}), 500

# Provision a new database
@app.route('/provision', methods=['POST'])
def provision():
    data = request.get_json()
    client_name = data.get("client_name")

    if not client_name:
        return jsonify({"error": "Client name is required"}), 400

    try:
        db_url = create_client_database(client_name)
        return jsonify({"message": "Database created", "db_url": db_url}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize database and run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
