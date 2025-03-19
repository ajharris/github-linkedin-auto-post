from flask import Flask, request, redirect, send_file
from models import db
import requests
import os

from dotenv import load_dotenv

from flask import send_from_directory


CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"  # Update for production


# Get absolute path of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicitly set the frontend build path
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend/build")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

app.config.from_object("config")
db.init_app(app)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):


    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    # Serve index.html for all unknown routes
    return send_from_directory(app.static_folder, "index.html")



load_dotenv()
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

@app.route("/auth/linkedin")
def linkedin_auth():
    linkedin_auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
    f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    f"&scope=w_member_social"
    )

    return redirect(linkedin_auth_url)

@app.route("/auth/linkedin/callback")
def linkedin_callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return f"LinkedIn OAuth error: {error}", 400

    if not code:
        return "Authorization failed: No code received from LinkedIn.", 400



    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return f"Failed to get access token: {response.text}", 400

    access_token = response.json().get("access_token")
    return f"Your LinkedIn Access Token: {access_token}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
