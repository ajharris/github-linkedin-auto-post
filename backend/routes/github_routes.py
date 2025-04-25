from flask import Blueprint, jsonify, request, redirect, current_app, url_for
from backend.models import db, User, GitHubEvent
from backend.services.verify_signature import verifyGITHUB_signature
from backend.services.post_to_linkedin import post_to_linkedin
import os
import requests

github_routes = Blueprint("github_routes", __name__)

@github_routes.route("/webhook/github", methods=["POST"])
def SECRET_GITHUB_webhook():
    if not request.data:
        current_app.logger.error("[Webhook] Missing payload in request.")
        return jsonify({"error": "Missing payload"}), 400

    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        current_app.logger.error("[Webhook] Missing signature header.")
        return jsonify({"error": "Invalid signature"}), 403

    if not verifyGITHUB_signature(request.data, signature):
        current_app.logger.error("[Webhook] Invalid signature.")
        return jsonify({"error": "Unauthorized"}), 403

    event_type = request.headers.get("X-GitHub-Event", None)
    if not event_type:
        current_app.logger.error("[Webhook] Missing event type header.")
        return jsonify({"error": "Missing event type"}), 400

    if event_type not in ["push", "pull_request"]:
        current_app.logger.info(f"[Webhook] Unsupported event type: {event_type}")
        return jsonify({"error": "Unsupported event type"}), 400

    payload = request.get_json()

    current_app.logger.info(f"[Webhook] Received event type: {event_type}")
    current_app.logger.info(f"[Webhook] Payload: {payload}")

    if event_type == "pull_request":
        current_app.logger.info("[Webhook] Pull request event received.")
        return jsonify({"message": "Pull request event received"}), 204

    repo = payload.get("repository", {}).get("name")
    commit_message = payload.get("head_commit", {}).get("message")
    user_id = payload.get("repository", {}).get("owner", {}).get("id") or payload.get(
        "pusher", {}
    ).get("name")

    current_app.logger.info(
        f"[Webhook] Extracted values → user_id: {user_id}, repo: {repo}, commit: {commit_message}"
    )

    if not repo or not commit_message or not user_id:
        current_app.logger.error("[Webhook] Missing required fields in payload.")
        return jsonify({"error": "Invalid payload"}), 400

    user = User.query.filter_by(SECRET_GITHUB_id=user_id).first()
    if not user:
        current_app.logger.warning("[Webhook] No user found.")
        return jsonify({"error": "No user found"}), 400

    current_app.logger.info(f"[Webhook] Found user: {user.SECRET_GITHUB_id}")

    existing_event = GitHubEvent.query.filter_by(
        user_id=user.id, repo_name=repo, commit_message=commit_message
    ).first()
    if existing_event:
        current_app.logger.info("[Webhook] Redundant event detected. Skipping.")
        return jsonify({"message": "Redundant event"}), 200

    current_app.logger.info(
        "[Webhook] Event is not redundant. Proceeding with LinkedIn post."
    )

    try:
        response = post_to_linkedin(user, repo, commit_message, payload)

        if response is None or not hasattr(response, "json"):
            current_app.logger.error(
                "[Webhook] Invalid response from post_to_linkedin."
            )
            return jsonify({"error": "Failed to post to LinkedIn"}), 500

        post_id = response.json().get("id")
        current_app.logger.info(f"[Webhook] LinkedIn post ID: {post_id}")

        event = GitHubEvent(
            user_id=user.id,
            repo_name=repo,
            commit_message=commit_message,
            commit_url=payload.get("head_commit", {}).get("url"),
            linkedin_post_id=post_id,
        )
        db.session.add(event)
        db.session.commit()

        current_app.logger.info("[Webhook] Event successfully saved to database.")
        return jsonify({"status": "success", "linkedin_post_id": post_id}), 200

    except ValueError as e:
        current_app.logger.error(f"[Webhook] Exception during post: {e}")
        return jsonify({"error": "An error occurred during processing"}), 500
    except Exception as e:
        current_app.logger.error(f"[Webhook] Unexpected exception: {e}")
        return jsonify({"error": "Internal server error"}), 500