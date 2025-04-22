import os
from functools import wraps
from flask import request, jsonify, current_app
from backend.models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        github_user_id = request.cookies.get("github_user_id")
        if not github_user_id:
            current_app.logger.error("[Auth] Missing github_user_id cookie.")
            return jsonify({"error": "Authentication required"}), 401

        user = User.query.filter_by(github_id=github_user_id).first()
        if not user:
            current_app.logger.error(f"[Auth] User with GitHub ID {github_user_id} not found.")
            return jsonify({"error": "Invalid session"}), 401

        # Attach the user to the request context for use in the route
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

# --- NEW: LinkedIn environment variable helpers ---

def get_linkedin_client_id():
    value = os.environ.get("LINKEDIN_CLIENT_ID", "")
    if not value:
        current_app.logger.warning("LINKEDIN_CLIENT_ID is missing or empty")
    return value

def get_linkedin_client_secret():
    value = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    if not value:
        current_app.logger.warning("LINKEDIN_CLIENT_SECRET is missing or empty")
    return value
