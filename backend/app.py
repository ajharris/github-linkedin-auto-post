from flask import Flask, request, jsonify
from auth import linkedin_oauth
from github_webhook import handle_github_event
from database_service import create_client_database
from models import db

app = Flask(__name__)

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # Main database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# LinkedIn OAuth Routes
app.register_blueprint(linkedin_oauth, url_prefix="/auth")

# GitHub Webhook Route
@app.route('/webhook/github', methods=['POST'])
def webhook():
    return handle_github_event()

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the main database is initialized
    app.run(debug=True)
