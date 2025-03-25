from flask import Blueprint, request, redirect, send_from_directory, jsonify
import requests
import os
from dotenv import load_dotenv
from backend.models import db, GitHubEvent, User
from datetime import datetime, timezone
import hmac
import hashlib
from backend.services.post_generator import generate_post_from_webhook

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
    secret = GITHUB_SECRET
    if not secret or not signature:
        return False
    secret = secret.encode()
    computed_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    print("✅ Webhook received")
    print("🔍 Headers:", dict(request.headers))
    print("🔍 Content-Type:", request.headers.get("Content-Type"))
    print("🔍 Raw payload:", request.get_data(as_text=True))

    payload = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256")

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ JSON parsing failed:", e)
        return jsonify({"error": "Invalid JSON"}), 400

    print("✅ Parsed data:", data)
    return jsonify({"status": "success"}), 200
    
