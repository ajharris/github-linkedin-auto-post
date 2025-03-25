from flask import Blueprint, request, redirect, send_from_directory, jsonify
import requests
import os
from dotenv import load_dotenv
from backend.models import db, GitHubEvent, User
from datetime import datetime, timezone
import hmac
import hashlib
from backend.services.post_generator import generate_post_from_webhook
from backend.services.post_to_linkedin import post_to_linkedin

import logging

logging.basicConfig(level=logging.INFO)

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
import hmac
import hashlib 

def verify_github_signature(request, signature):
    if not signature:
        return False  

    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode("utf-8")
    payload = request.data

    computed_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)





@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_github_signature(request, signature):
        return jsonify({"error": "Invalid signature"}), 403

    logging.info("Webhook received")

    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Invalid JSON"}), 400

    print("✅ Parsed data:", data)

    # 🔍 Extract user and commit info
    pusher_name = data.get("pusher", {}).get("name")
    repo_name = data.get("repository", {}).get("full_name")
    commit_message = data.get("head_commit", {}).get("message")
    commit_url = data.get("head_commit", {}).get("url")

    # 🔐 Look up the user
    user = User.query.filter_by(github_id=pusher_name).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 📝 Create GitHubEvent
    linkedin_post_id = None
    linkedin_response = post_to_linkedin(repo_name, commit_message)

    if linkedin_response and isinstance(linkedin_response, dict):
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
