from flask import Blueprint, request, redirect, send_from_directory, jsonify
import os
import requests
import logging
from dotenv import load_dotenv
from backend.models import db, GitHubEvent, User
from backend.services.post_generator import generate_post_from_webhook
from backend.services.post_to_linkedin import post_to_linkedin
from backend.services.verify_signature import verify_github_signature

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# LinkedIn OAuth settings
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"

# Define Blueprint
routes = Blueprint("routes", __name__)

# -------------------- FRONTEND SERVING -------------------- #
@routes.route("/", defaults={"path": ""})
@routes.route("/<path:path>")
def serve(path):
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/build")
    file_path = os.path.join(frontend_dir, path)
    if path and os.path.exists(file_path):
        return send_from_directory(frontend_dir, path)
    return send_from_directory(frontend_dir, "index.html")


# -------------------- LINKEDIN AUTHENTICATION -------------------- #
@routes.route("/auth/linkedin")
def linkedin_auth():
    """Redirects user to LinkedIn OAuth authorization URL"""
    linkedin_auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=w_member_social"
    )
    return redirect(linkedin_auth_url)

@routes.route("/auth/linkedin/callback")
def linkedin_callback():
    """Handles LinkedIn OAuth callback"""
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return f"LinkedIn OAuth error: {error}", 400
    if not code:
        return "Authorization failed: No code received from LinkedIn.", 400

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return f"Failed to get access token: {response.text}", 400

    access_token = response.json().get("access_token")
    return f"Your LinkedIn Access Token: {access_token}"


# -------------------- GITHUB WEBHOOK HANDLING -------------------- #
@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_github_signature(request, signature):
        return jsonify({"error": "Invalid signature"}), 403

    logging.info("Webhook received")

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    print("✅ Parsed data:", data)

    # Validate required fields
    pusher = data.get("pusher", {})
    repo = data.get("repository", {})
    head_commit = data.get("head_commit", {})

    if not pusher or not repo or not head_commit:
        return jsonify({"error": "Missing required data"}), 400

    pusher_name = pusher.get("name")
    repo_name = repo.get("full_name")
    commit_message = head_commit.get("message")
    commit_url = head_commit.get("url")

    if not all([pusher_name, repo_name, commit_message, commit_url]):
        return jsonify({"error": "Incomplete commit info"}), 400

    user = User.query.filter_by(github_id=pusher_name).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    linkedin_post_id = None
    linkedin_response = post_to_linkedin(repo_name, commit_message)
    if isinstance(linkedin_response, dict):
        linkedin_post_id = linkedin_response.get("id")

    github_event = GitHubEvent(
        user_id=user.id,
        repo_name=repo_name,
        commit_message=commit_message,
        commit_url=commit_url,
        event_type="push",
        linkedin_post_id=linkedin_post_id
    )

    db.session.add(github_event)
    db.session.commit()

    return jsonify({"status": "success"}), 200

    return jsonify({"status": "success"}), 200

