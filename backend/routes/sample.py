from flask import Blueprint, jsonify, request

sample_bp = Blueprint("sample", __name__)

@sample_bp.route("/sample-endpoint", methods=["POST"])
def sample_endpoint():
    data = request.get_json()
    return jsonify({"message": "Success", "received": data}), 200
