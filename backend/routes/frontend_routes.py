from flask import Blueprint, jsonify, send_from_directory
import os

frontend_routes = Blueprint("frontend_routes", __name__)

@frontend_routes.route("/", defaults={"path": ""})
@frontend_routes.route("/<path:path>")
def serve(path):
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../frontend/build")
    )
    file_path = os.path.normpath(os.path.join(frontend_dir, path or "index.html"))

    if not file_path.startswith(frontend_dir):
        return jsonify({"error": "Forbidden"}), 403

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(frontend_dir, path or "index.html")

    return jsonify(error="File not found"), 404