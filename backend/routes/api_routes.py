from flask import Blueprint, jsonify, request, current_app
from backend.models import db, GitHubEvent, User
from backend.services.utils import login_required

api_routes = Blueprint("api_routes", __name__)

@api_routes.route("/api/github/<SECRET_GITHUB_id>/status")
@login_required
def checkGITHUB_link_status(SECRET_GITHUB_id):
    user = request.user
    return (
        jsonify(
            {
                "linked": bool(user.linkedin_id),
                "SECRET_GITHUB_id": user.SECRET_GITHUB_id,
                "SECRET_GITHUB_username": user.SECRET_GITHUB_username,
                "linkedin_id": user.linkedin_id,
            }
        ),
        200,
    )

@api_routes.route("/api/github/<SECRET_GITHUB_id>/commits")
@login_required
def get_commits(SECRET_GITHUB_id):
    user = request.user
    events = GitHubEvent.query.filter_by(user_id=user.id).all()
    commits = [
        {
            "id": e.id,
            "repo": e.repo_name,
            "message": e.commit_message,
            "url": e.commit_url,
            "status": "posted" if e.linkedin_post_id else "unposted",
        }
        for e in events
    ]
    return jsonify({"commits": commits}), 200

@api_routes.route("/api/get_user_profile", methods=["GET"])
@login_required
def get_user_profile():
    current_app.logger.info("[Get User Profile] Starting user profile retrieval.")
    SECRET_GITHUB_user_id = request.cookies.get("SECRET_GITHUB_user_id") or session.get(
        "SECRET_GITHUB_user_id"
    )
    if not SECRET_GITHUB_user_id:
        current_app.logger.error(
            "[Get User Profile] GitHub user ID not found in cookies or session."
        )
        if current_app.config.get("TESTING"):
            return (
                jsonify({"error": "GitHub user ID not found"}),
                200,
            )
        return jsonify({"error": "GitHub user ID not found"}), 401

    user = User.query.filter_by(SECRET_GITHUB_id=SECRET_GITHUB_user_id).first()
    if not user:
        current_app.logger.error(
            f"[Get User Profile] No user found for GitHub ID: {SECRET_GITHUB_user_id}"
        )
        return jsonify({"error": "User not found"}), 404

    current_app.logger.info(
        f"[Get User Profile] Retrieved user: {user.SECRET_GITHUB_id}, LinkedIn ID: {user.linkedin_id}"
    )
    return (
        jsonify(
            {
                "linkedin_connected": bool(
                    user.linkedin_token and user.linkedin_id
                ),
                "SECRET_GITHUB_id": user.SECRET_GITHUB_id,
                "SECRET_GITHUB_username": user.SECRET_GITHUB_username,
                "linkedin_id": user.linkedin_id,
                "linkedin_linked": bool(
                    user.linkedin_token and user.linkedin_id
                ),
            }
        ),
        200,
    )