from flask import Blueprint, request, jsonify
from backend.github_webhook import handle_github_event

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/github', methods=['POST'])
def webhook():
    """Handle incoming GitHub webhooks."""
    if 'handle_github_event' in globals():
        return handle_github_event()
    return jsonify({"error": "GitHub webhook handler not implemented"}), 500
