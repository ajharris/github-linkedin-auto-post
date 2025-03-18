from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.extensions import db
from backend.models import GitHubEvent

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

@webhook_bp.route("/", methods=["POST"])
def github_webhook():
    """Handle GitHub webhook events."""
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400

    event_type = request.headers.get("X-GitHub-Event", "unknown")

    if event_type == "push":
        repo_name = data.get("repository", {}).get("full_name", "unknown")
        commits = data.get("commits", [])

        for commit in commits:
            # ✅ Convert timestamp string to Python datetime
            timestamp_str = commit.get("timestamp", None)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ") if timestamp_str else None

            new_event = GitHubEvent(
                repo=repo_name,
                commit_message=commit.get("message"),
                author=commit.get("author", {}).get("name"),
                url=commit.get("url"),
                timestamp=timestamp,  # ✅ Use proper datetime format
            )
            db.session.add(new_event)

        db.session.commit()  # ✅ Ensure the changes are saved

        return jsonify({"status": "success", "message": "Webhook received"}), 200

    return jsonify({"status": "ignored", "message": "Unhandled event type"}), 200
