from flask import Blueprint

linkedin_oauth = Blueprint("linkedin_oauth", __name__)

@linkedin_oauth.route("/login")
def login():
    return "LinkedIn OAuth login route (not implemented yet)"
