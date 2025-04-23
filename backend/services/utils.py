import os
from functools import wraps
from flask import request, jsonify, current_app
from backend.models import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        SECRET_GITHUB_user_id = request.cookies.get("SECRET_GITHUB_user_id")
        if not SECRET_GITHUB_user_id:
            current_app.logger.error("[Auth] Missing SECRET_GITHUB_user_id cookie.")
            return jsonify({"error": "Authentication required"}), 401

        user = User.query.filter_by(SECRET_GITHUB_id=SECRET_GITHUB_user_id).first()
        if not user:
            current_app.logger.error(
                f"[Auth] User with GitHub ID {SECRET_GITHUB_user_id} not found."
            )
            return jsonify({"error": "Invalid session"}), 401

        # Attach the user to the request context for use in the route
        request.user = user
        return f(*args, **kwargs)

    return decorated_function


# --- NEW: LinkedIn environment variable helpers ---


# Ensure get_linkedin_client_id and get_linkedin_client_secret return default values if environment variables are missing
def get_linkedin_client_id():
    return os.getenv("LINKEDIN_CLIENT_ID", "default_client_id")


def get_linkedin_client_secret():
    return os.getenv("LINKEDIN_CLIENT_SECRET", "default_client_secret")
