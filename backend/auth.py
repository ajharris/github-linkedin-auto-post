from flask import Blueprint, jsonify

linkedin_oauth = Blueprint('linkedin_oauth', __name__)

@linkedin_oauth.route('/login', methods=['GET'])
def login():
    """Mock LinkedIn OAuth login."""
    return jsonify({"message": "LinkedIn OAuth login endpoint"})
