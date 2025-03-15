from flask import Blueprint, jsonify, request

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/", methods=["POST"])  # Ensure trailing slash
def webhook_handler():
    data = request.get_json()
    return jsonify({"message": "Webhook received", "event": data}), 200
