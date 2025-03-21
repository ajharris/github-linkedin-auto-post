from flask import Blueprint, request, redirect, send_from_directory, jsonify
import requests
import os
from dotenv import load_dotenv
from backend.models import db, GitHubEvent, User
from datetime import datetime, timezone
import hmac
import hashlib

# Load environment variables
load_dotenv()

# LinkedIn OAuth settings
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"

# GitHub Webhook Secret
GITHUB_SECRET = os.getenv("GITHUB_SECRET")

# Define Blueprint for routes
routes = Blueprint("routes", __name__)

### -------------------- FRONTEND SERVING -------------------- ###
@routes.route("/", defaults={"path": ""})
@routes.route("/<path:path>")
def serve(path):
    """Serve frontend static files"""
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/build")
    
    if path and os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)

    return send_from_directory(frontend_dir, "index.html")


### -------------------- LINKEDIN AUTHENTICATION -------------------- ###
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


### -------------------- GITHUB WEBHOOK HANDLING -------------------- ###
def verify_github_signature(payload, signature):
    """Verifies GitHub webhook signature using HMAC"""
    secret = os.getenv("GITHUB_SECRET")

    if not secret or not signature:
        return False  # Reject if no secret or signature is provided

    secret = secret.encode()  # ✅ Ensure the secret is properly encoded
    computed_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)


@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    """Handles incoming GitHub webhook events with security"""
    payload = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256")

    # 🔐 Verify webhook signature
    if not verify_github_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    event_type = request.headers.get("X-GitHub-Event", "ping")
    repo_name = data.get("repository", {}).get("full_name", "unknown_repo")

    if event_type == "push":
        commit_message = data["head_commit"]["message"]
        commit_url = data["head_commit"]["url"]
        pusher = data["pusher"]["name"]
    elif event_type == "release":
        commit_message = f"New release: {data['release']['name']}"
        commit_url = data["release"]["html_url"]
        pusher = data["release"]["author"]["login"]
    else:
        return jsonify({"message": "Event type not supported"}), 200


    user = User.query.filter_by(github_id=pusher).first()
    if not user:
        return jsonify({"error": "User not linked to GitHub"}), 404

    event = GitHubEvent(
        user_id=user.id,
        repo_name=repo_name,
        commit_message=commit_message,
        commit_url=commit_url,
        status="pending",
        timestamp=datetime.now(timezone.utc)  # Ensure events are stored with a timestamp
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({"message": f"GitHub {event_type} event stored successfully", "commit_url": commit_url}), 200
