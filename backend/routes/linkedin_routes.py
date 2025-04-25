from flask import Blueprint, jsonify, request, redirect, session, current_app
from backend.models import db, User
from backend.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET
import os
import requests
import uuid
from urllib.parse import urlparse

linkedin_routes = Blueprint("linkedin_routes", __name__)

@linkedin_routes.route("/auth/linkedin", methods=["GET", "POST"])
def linkedin_auth():
    if request.method == "POST":
        return jsonify({"message": "LinkedIn account linked successfully."}), 200

    SECRET_GITHUB_user_id = request.cookies.get("SECRET_GITHUB_user_id") or session.get("SECRET_GITHUB_user_id")
    if not SECRET_GITHUB_user_id:
        current_app.logger.error("[LinkedIn] GitHub user ID not found in cookies or session.")
        return jsonify({"error": "GitHub user ID not found"}), 401

    CLIENT_ID = current_app.config.get("LINKEDIN_CLIENT_ID", "").strip()
    REDIRECT_URI = current_app.config.get("LINKEDIN_REDIRECT_URI", "").strip()
    state = str(uuid.uuid4())
    session["linkedin_state"] = state
    current_app.logger.info(f"[LinkedIn] Generated state for LinkedIn auth: {state}")

    try:
        user = User.query.filter_by(SECRET_GITHUB_id=SECRET_GITHUB_user_id).first()
        if user:
            user.linkedin_token = None
            user.linkedin_id = None
            db.session.commit()
            current_app.logger.info(
                f"[LinkedIn] Cleared LinkedIn token and ID for GitHub user {SECRET_GITHUB_user_id}"
            )

        scope = "w_member_social"
        linkedin_auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={scope}"
            f"&state={state}"
        )
        current_app.logger.info(f"[LinkedIn] Generated auth URL: {linkedin_auth_url}")

        parsed_url = urlparse(linkedin_auth_url)
        if not (
            parsed_url.scheme == "https"
            and parsed_url.netloc == "www.linkedin.com"
            and parsed_url.path == "/oauth/v2/authorization"
        ):
            current_app.logger.error(
                f"[LinkedIn] Invalid redirect URL: {linkedin_auth_url}"
            )
            return jsonify({"error": "Invalid redirect URL"}), 400
        return redirect(linkedin_auth_url)
    except Exception as e:
        current_app.logger.error(f"[LinkedIn] Error generating auth URL: {e}")
        return jsonify({"error": "Failed to generate LinkedIn auth URL"}), 500