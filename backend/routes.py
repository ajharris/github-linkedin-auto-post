from flask import Blueprint, request, redirect, send_from_directory, jsonify, current_app
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
    linkedin_auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=r_liteprofile%20w_member_social"
        f"&state={github_user_id}"
    )
    return redirect(linkedin_auth_url)

@routes.route("/auth/linkedin/callback")
def linkedin_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    github_user_id = request.args.get("state")

    if error:
        return f"LinkedIn OAuth error: {error}", 400
    if not code or not github_user_id:
        return "Authorization failed", 400

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

    if token_response.status_code != 200:
        return f"Failed to get access token: {token_response.text}", 400

    access_token = token_response.json().get("access_token")
    if not access_token:
        return "Missing access token from LinkedIn", 400

    # ✅ GET REAL LINKEDIN ID
    profile_response = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if profile_response.status_code != 200:
        return f"Failed to fetch LinkedIn profile: {profile_response.text}", 400

    linkedin_user_id = profile_response.json().get("id")
    if not linkedin_user_id:
        return "LinkedIn profile missing ID", 400

    user = User.query.filter_by(github_id=github_user_id).first()
    if not user:
        # 👇 Optionally auto-create user here instead of returning 404
        user = User(github_id=github_user_id)

    user.linkedin_token = access_token
    user.linkedin_id = linkedin_user_id
    db.session.add(user)
    db.session.commit()

    current_app.logger.info(f"[LinkedIn] Linked user {github_user_id} with LinkedIn ID {linkedin_user_id}")
    return "✅ LinkedIn Access Token stored successfully. You can close this window."



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

    github_user_id = str(repo.get("owner", {}).get("id") or pusher_name)

    logging.info(f"Looking for user with github_id={github_user_id}")
    user = User.query.filter_by(github_id=github_user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    logging.info(f"Webhook user: {user}, LinkedIn ID: {user.linkedin_id}")

    linkedin_post_id = None
    try:
        linkedin_response = post_to_linkedin(user, repo_name, commit_message)
        if isinstance(linkedin_response, dict):
            linkedin_post_id = linkedin_response.get("id")
    except ValueError as e:
        logging.exception("Failed to post to LinkedIn: {e}")
        return jsonify({"error": str(e)}), 500

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

    logging.info(f"[Webhook] Posting to LinkedIn for repo: {repo_name}, commit: {commit_message}")

    if isinstance(linkedin_response, requests.Response):
        logging.info(f"[LinkedIn] Status: {linkedin_response.status_code}")
        logging.info(f"[LinkedIn] Response: {linkedin_response.text}")

    return jsonify({"status": "success"}), 200

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

    # Redirect to LinkedIn auth with github_user_id as state
    return redirect(f"/auth/linkedin?github_user_id={github_user_id}")

