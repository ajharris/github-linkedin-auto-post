from flask import Blueprint, json, request, redirect, send_from_directory, jsonify, current_app
import os
import requests
import logging
from dotenv import load_dotenv
from backend.models import db, GitHubEvent, User
from backend.services.post_generator import generate_post_from_webhook
from backend.services.post_to_linkedin import post_to_linkedin
from backend.services.verify_signature import verify_github_signature
import jwt  # Install with `pip install pyjwt`
from jwt.exceptions import InvalidTokenError

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"

routes = Blueprint("routes", __name__)

# -------------------- FRONTEND SERVING -------------------- #
@routes.route("/", defaults={"path": ""})
@routes.route("/<path:path>")
def serve(path):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/build"))
    file_path = os.path.normpath(os.path.join(frontend_dir, path or "index.html"))

    if not file_path.startswith(frontend_dir):
        return jsonify({"error": "Forbidden"}), 403

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(frontend_dir, path or "index.html")

    return jsonify(error="File not found"), 404


# -------------------- LINKEDIN AUTHENTICATION -------------------- #
@routes.route("/auth/linkedin")
def linkedin_auth():
    github_user_id = request.args.get("github_user_id", "test")
    current_app.logger.info(f"[LinkedIn] Received request to link LinkedIn for GitHub user ID: {github_user_id}")

    try:
        user = User.query.filter_by(github_id=github_user_id).first()
        if user:
            user.linkedin_token = None
            user.linkedin_id = None
            db.session.commit()
            current_app.logger.info(f"[LinkedIn] Cleared LinkedIn token and ID for GitHub user {github_user_id}")

        scope = "w_member_social"
        linkedin_auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={scope}"
            f"&state={github_user_id}"
        )
        current_app.logger.info(f"[LinkedIn] Generated auth URL: {linkedin_auth_url}")
        return redirect(linkedin_auth_url)
    except Exception as e:
        current_app.logger.error(f"[LinkedIn] Error generating auth URL: {e}")
        return jsonify({"error": "Failed to generate LinkedIn auth URL"}), 500


@routes.route("/auth/linkedin/callback")
def linkedin_callback():
    current_app.logger.info("[LinkedIn] Received callback request.")
    current_app.logger.info(f"[LinkedIn] Request args: {request.args}")

    error = request.args.get("error")
    error_description = request.args.get("error_description", "No description provided")

    if error:
        current_app.logger.error(f"[LinkedIn] OAuth error: {error}")
        current_app.logger.error(f"[LinkedIn] Error description: {error_description}")
        return f"LinkedIn OAuth error: {error} - {error_description}", 400

    code = request.args.get("code")
    github_user_id = request.args.get("state")

    if not code or not github_user_id:
        current_app.logger.error("[LinkedIn] Missing authorization code or GitHub user ID.")
        return "Authorization failed", 400

    current_app.logger.info(f"[LinkedIn] Authorization code received: {code}")
    current_app.logger.info(f"[LinkedIn] GitHub user ID: {github_user_id}")

    try:
        token_response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )
        current_app.logger.info(f"[LinkedIn] Token response status: {token_response.status_code}")
        current_app.logger.info(f"[LinkedIn] Token response body: {token_response.text}")

        if token_response.status_code != 200:
            return f"Failed to get access token: {token_response.text}", 400

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        id_token = token_data.get("id_token")  # OpenID Connect ID token

        if not access_token or not id_token:
            current_app.logger.error("[LinkedIn] Missing access token or ID token.")
            return "Missing access token or ID token from LinkedIn", 400

        # Verify the ID token
        try:
            decoded_id_token = jwt.decode(
                id_token,
                options={"verify_signature": False},  # LinkedIn does not provide a public key for signature verification
                algorithms=["RS256"]
            )
            linkedin_user_id = decoded_id_token.get("sub")
            current_app.logger.info(f"[LinkedIn] Decoded ID token: {decoded_id_token}")
        except InvalidTokenError as e:
            current_app.logger.error(f"[LinkedIn] Invalid ID token: {e}")
            return "Invalid ID token", 400

        user = User.query.filter_by(github_id=github_user_id).first()
        if not user:
            current_app.logger.warning("[LinkedIn] No user found with GitHub ID. Aborting.")
            return "GitHub login required before connecting LinkedIn.", 400

        user.linkedin_token = access_token
        user.linkedin_id = linkedin_user_id

        db.session.commit()

        current_app.logger.info(f"[LinkedIn] Stored token and ID for GitHub user {github_user_id}")
        return "✅ LinkedIn Access Token and ID stored successfully. You can close this window."
    except Exception as e:
        current_app.logger.error(f"[LinkedIn] Error during callback processing: {e}")
        return jsonify({"error": "Failed to process LinkedIn callback"}), 500


# -------------------- GITHUB WEBHOOK HANDLING -------------------- #
def is_linkedin_token_valid(access_token):
    """Validate LinkedIn access token."""
    try:
        response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 200:
            return True
        else:
            current_app.logger.warning(
                f"[LinkedIn Token Validation] Token validation failed with status code {response.status_code}. "
                f"Response: {response.text}"
            )
            return False
    except requests.RequestException as e:
        current_app.logger.error(f"[LinkedIn Token Validation] Exception occurred: {e}")
        return False

def is_github_token_valid(access_token):
    """Validate GitHub access token."""
    response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    )
    return response.status_code == 200

@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    payload = request.get_json()

    if not payload:
        current_app.logger.error("[Webhook] Missing payload in request.")
        return jsonify({"error": "Missing payload"}), 400

    github_user_id = (
        str(payload.get("sender", {}).get("id"))
        or str(payload.get("repository", {}).get("owner", {}).get("id"))
        or str(payload.get("pusher", {}).get("name"))
    )

    repo_name = payload.get("repository", {}).get("name")
    commit_message = payload.get("head_commit", {}).get("message")
    commit_url = payload.get("head_commit", {}).get("url")

    if not github_user_id or not repo_name or not commit_message:
        current_app.logger.error("[Webhook] Missing required fields in payload.")
        return jsonify({"error": "Invalid payload"}), 400

    current_app.logger.info(f"[Webhook] Extracted values → user_id: {github_user_id}, repo: {repo_name}, commit: {commit_message}")

    user = User.query.filter_by(github_id=github_user_id).first()
    if not user:
        current_app.logger.warning("[Webhook] No user found.")
        return jsonify({"error": "No user found"}), 400

    # Record the commit in the database
    github_event = GitHubEvent(
        user_id=user.id,
        repo_name=repo_name,
        commit_message=commit_message,
        commit_url=commit_url,
        event_type="push",
        status="pending"
    )
    db.session.add(github_event)
    db.session.commit()
    current_app.logger.info(f"[Webhook] Commit recorded in database with ID: {github_event.id}")

    return jsonify({"status": "success"})


@routes.route("/auth/github/callback")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
        },
        headers={"Accept": "application/json"}
    )

    token_json = token_resp.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return "Failed to obtain GitHub access token", 400

    user_resp = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {access_token}"}
    )
    github_data = user_resp.json()
    github_user_id = str(github_data.get("id"))
    github_username = github_data.get("login")

    user = User.query.filter_by(github_id=github_user_id).first()
    if not user:
        user = User(github_id=github_user_id)

    user.github_token = access_token
    user.github_username = github_username
    db.session.add(user)
    db.session.commit()

    # Use the FRONTEND_URL environment variable for the redirect
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return redirect(f"{frontend_url}?github_user_id={github_user_id}")


@routes.route("/api/github/<github_id>/status")
def check_github_link_status(github_id):
    user = User.query.filter_by(github_id=str(github_id)).first()
    if user:
        return jsonify({
            "linked": bool(user.linkedin_id),
            "github_id": user.github_id,
            "github_username": user.github_username,
            "linkedin_id": user.linkedin_id
        })
    return jsonify({"linked": False}), 404


@routes.route("/debug/fetch_linkedin_id")
def debug_fetch_linkedin_id():
    try:
        github_user_id = request.args.get("github_user_id")
    except (TypeError, ValueError):
        return "Invalid github_user_id parameter", 400

    user = User.query.filter_by(github_id=github_user_id).first()
    if not user or not user.linkedin_token or not is_linkedin_token_valid(user.linkedin_token):
        return f"No valid LinkedIn token found for GitHub user {github_user_id}", 404

    access_token = user.linkedin_token
    profile_response = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if profile_response.status_code != 200:
        return f"Failed to fetch LinkedIn profile: {profile_response.text}", 400

    linkedin_id = profile_response.json().get("id")
    if not linkedin_id:
        return "LinkedIn profile missing ID", 400

    user.linkedin_id = f"urn:li:person:{linkedin_id}"
    db.session.commit()

    return f"✅ Updated LinkedIn ID to {user.linkedin_id} for GitHub user {github_user_id}"


@routes.route("/api/github/<github_id>/commits")
def get_commits(github_id):
    user = User.query.filter_by(github_id=str(github_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Filter for commits that haven't been posted to LinkedIn
    events = GitHubEvent.query.filter_by(user_id=user.id, status="pending").order_by(GitHubEvent.timestamp.desc()).all()
    commits = [
        {
            "id": event.id,
            "repo_name": event.repo_name,
            "message": event.commit_message,
            "timestamp": event.timestamp.isoformat(),
        }
        for event in events
    ]
    return jsonify({"commits": commits})

@routes.route("/api/github/<github_id>/post_commit", methods=["POST"])
def post_commit_to_linkedin(github_id):
    user = User.query.filter_by(github_id=str(github_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.linkedin_token or not is_linkedin_token_valid(user.linkedin_token):
        return jsonify({"error": "Invalid or missing LinkedIn token"}), 400

    data = request.get_json()
    commit_id = data.get("commit_id")
    if not commit_id:
        return jsonify({"error": "Missing commit ID"}), 400

    commit = GitHubEvent.query.filter_by(id=commit_id, user_id=user.id).first()
    if not commit:
        return jsonify({"error": "Commit not found"}), 404

    try:
        post_to_linkedin(user, commit.repo_name, commit.commit_message)
        commit.status = "posted"
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        current_app.logger.error(f"[Post Commit] Failed to post to LinkedIn: {e}")
        return jsonify({"error": str(e)}), 500

@routes.route("/api/github/<github_id>/disconnect_linkedin", methods=["POST"])
def disconnect_linkedin(github_id):
    user = User.query.filter_by(github_id=str(github_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Remove LinkedIn token and ID from the database
    user.linkedin_token = None
    user.linkedin_id = None
    db.session.commit()

    current_app.logger.info(f"[LinkedIn] Disconnected LinkedIn for GitHub user {github_id}")
    return jsonify({"status": "success"})
