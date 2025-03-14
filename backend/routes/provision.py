from flask import Blueprint, request, jsonify
from database_service import create_client_database

provision_bp = Blueprint('provision', __name__)

@provision_bp.route('/', methods=['POST'])
def provision():
    """Provision a new database for a client."""
    data = request.get_json()
    client_name = data.get("client_name")

    if not client_name:
        return jsonify({"error": "Client name is required"}), 400

    try:
        db_url = create_client_database(client_name)
        return jsonify({"message": "Database created", "db_url": db_url}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
