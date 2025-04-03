from flask import Blueprint, json, request, redirect, send_from_directory, jsonify, current_app
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
    print("💬 LinkedIn callback args:", dict(request.args))

    github_user_id = request.args.get("github_user_id", "test")
    linkedin_auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
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

    # Store the token without fetching /me
    user = User.query.filter_by(github_id=github_user_id).first()
    if not user:
        user = User(github_id=github_user_id)

    user.linkedin_token = access_token

    # ✅ Manually set your LinkedIn URN here once for testing
    user.linkedin_id = "urn:li:person:REPLACE_WITH_YOUR_URN"

    db.session.add(user)
    db.session.commit()

    current_app.logger.info(f"[LinkedIn] Stored token for GitHub user {github_user_id}")
    return "✅ LinkedIn Access Token stored successfully. You can close this window."



# -------------------- GITHUB WEBHOOK HANDLING -------------------- #
@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    payload = request.get_json()


    github_user_id = str(payload.get("sender", {}).get("id"))
    repo_name = payload.get("repository", {}).get("name")
    commit_message = payload.get("head_commit", {}).get("message")

    current_app.logger.info(f"[Webhook] Extracted values → user_id: {github_user_id}, repo: {repo_name}, commit: {commit_message}")

    user = User.query.filter_by(github_id=github_user_id).first()
    if not user:
        current_app.logger.warning(f"[Webhook] No user found for GitHub ID {github_user_id}")
        user = User.query.first()  # TEMP fallback for testing
        current_app.logger.warning(f"[Webhook] Fallback user: {user.github_id}")

    if not user.linkedin_token:
        current_app.logger.warning(f"[Webhook] No LinkedIn token for user {user.github_id}")
        return "No LinkedIn token", 200

    try:
        post_to_linkedin(user, repo_name, commit_message)
        current_app.logger.info("[Webhook] Post triggered successfully")
    except Exception as e:
        current_app.logger.error(f"[Webhook] Failed to post to LinkedIn: {e}")
        return str(e), 500

    return "OK", 200

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
    user.github_username = github_username  # ✅ Add this line
    db.session.add(user)
    db.session.commit()



    # Redirect to LinkedIn auth with github_user_id as state
    return redirect(f"/auth/linkedin?github_user_id={github_user_id}")

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
    if not user or not user.linkedin_token:
        return f"No LinkedIn token found for GitHub user {github_user_id}", 404

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

