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

        if not access_token:
            current_app.logger.error("[LinkedIn] Missing access token.")
            return "Missing access token from LinkedIn", 400

        id_token = token_data.get("id_token")
        if not id_token:
            current_app.logger.warning("[LinkedIn] Missing ID token. Proceeding without it.")
            id_token = None  # Allow processing to continue without ID token

        # Decode the ID token if present
        linkedin_user_id = None
        if id_token:
            try:
                decoded_id_token = jwt.decode(
                    id_token,
                    options={"verify_signature": False},  # LinkedIn does not provide public keys for verification
                    algorithms=["RS256"]
                )
                linkedin_user_id = decoded_id_token.get("sub")
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
@routes.route("/webhook/github", methods=["POST"])
def github_webhook():
    if not request.data:
        current_app.logger.error("[Webhook] Missing payload in request.")
        return jsonify({"error": "Missing payload"}), 400

    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        current_app.logger.error("[Webhook] Missing signature header.")
        return jsonify({"error": "Invalid signature"}), 403

    if not verify_github_signature(request.data, signature):
        current_app.logger.error("[Webhook] Invalid signature.")
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json()

    repo = payload.get("repository", {}).get("name")
    commit_message = payload.get("head_commit", {}).get("message")
    user_id = (
        payload.get("repository", {}).get("owner", {}).get("id")
        or payload.get("pusher", {}).get("name")
    )

    current_app.logger.info(f"[Webhook] Extracted values → user_id: {user_id}, repo: {repo}, commit: {commit_message}")

    if not repo or not commit_message or not user_id:
        current_app.logger.error("[Webhook] Missing required fields in payload.")
        return jsonify({"error": "Invalid payload"}), 400

    user = User.query.filter_by(github_id=user_id).first()
    if not user:
        current_app.logger.warning("[Webhook] No user found.")
        return jsonify({"error": "No user found"}), 400

    try:
        response = post_to_linkedin(user, repo, commit_message, payload)
        post_id = response.json().get("id")

        # Save to DB
        event = GitHubEvent(
            user_id=user.id,
            repo_name=repo,
            commit_message=commit_message,
            commit_url=payload.get("head_commit", {}).get("url"),
            linkedin_post_id=post_id
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({"status": "success", "linkedin_post_id": post_id}), 200

    except ValueError as e:
        current_app.logger.error(f"[Webhook] Exception during post: {e}")
        return jsonify({"error": "An error occurred during processing"}), 500
    except Exception as e:
        current_app.logger.error(f"[Webhook] Unexpected exception: {e}")
        return jsonify({"error": "Internal server error"}), 500


@routes.route("/api/github/<github_id>/status")
def check_github_link_status(github_id):
    user = User.query.filter_by(github_id=str(github_id)).first()
    if user:
        return jsonify({
            "linked": bool(user.linkedin_id),
            "github_id": user.github_id,
            "github_username": user.github_username,
            "linkedin_id": user.linkedin_id
        }), 200
    return jsonify({"error": "User not found"}), 404

@routes.route("/auth/github/callback")
@routes.route("/auth/github/callback")
def github_callback():
    from urllib.parse import urlencode

    code = request.args.get("code")
    if not code:
        current_app.logger.error("[GitHub] Missing authorization code.")
        return "Missing code from GitHub", 400

    current_app.logger.info(f"[GitHub] Received code: {code}")

    token_url = "https://github.com/login/oauth/access_token"
    user_url = "https://api.github.com/user"

    try:
        # Step 1: Exchange code for access token
        token_res = requests.post(
            token_url,
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "code": code,
            },
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            current_app.logger.error(f"[GitHub] Failed to get token: {token_data}")
            return "Failed to obtain GitHub access token", 400

        # Step 2: Fetch GitHub user info
        user_res = requests.get(
            user_url,
            headers={"Authorization": f"token {access_token}"}
        )

        user_data = user_res.json()
        github_id = user_data.get("id")
        github_username = user_data.get("login")

        if not github_id:
            current_app.logger.error("[GitHub] Missing GitHub ID in user response")
            return "GitHub user information is incomplete", 400

        # Step 3: Store or update user in DB
        user = User.query.filter_by(github_id=str(github_id)).first()
        if not user:
            user = User(
                github_id=str(github_id),
                github_username=github_username
            )
            db.session.add(user)
        else:
            user.github_username = github_username

        db.session.commit()

        # Step 4: Redirect frontend with GitHub user ID
        redirect_url = f"/?{urlencode({'github_user_id': github_id})}"
        return redirect(redirect_url)

    except Exception as e:
        current_app.logger.error(f"[GitHub] OAuth flow failed: {e}")
        return jsonify({"error": "GitHub OAuth error"}), 500

@routes.route("/routes")
def list_routes():
    from flask import url_for
    output = []
    for rule in current_app.url_map.iter_rules():
        output.append(f"{rule.endpoint}: {rule.rule}")
    return jsonify(sorted(output))
# -------------------- CLI COMMANDS -------------------- #
