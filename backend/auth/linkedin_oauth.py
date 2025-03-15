from flask import Blueprint, jsonify

linkedin_oauth = Blueprint("linkedin_oauth", __name__)

@linkedin_oauth.route("/", methods=["GET"], strict_slashes=False)  # Allow both /auth and /auth/
def auth_index():
    return jsonify({"message": "Auth system working"}), 200
