import os
from dotenv import load_dotenv
import logging
import requests

load_dotenv()

CLIENT_ID = "os.getenv('LINKEDIN_CLIENT_ID', '').strip()"
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"


def build_linkedin_auth_url(SECRET_GITHUB_user_id: str) -> str:
    if not CLIENT_ID():
        logging.error("[LinkedIn OAuth] CLIENT_ID is not set in environment variables.")
        raise ValueError("Missing LinkedIn CLIENT_ID")

    return (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={CLIENT_ID()}&redirect_uri={REDIRECT_URI}"
        f"&scope=w_member_social"  # Only request w_member_social
        f"&state={SECRET_GITHUB_user_id}"
    )


def exchange_code_for_access_token(auth_code: str) -> str:
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID(),  # Ensure client_id is included
        "client_secret": CLIENT_SECRET,  # Ensure client_secret is included
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)
    response_data = response.json()

    if response.status_code != 200:
        logging.error(
            f"[LinkedIn OAuth] Failed to exchange code for access token: {response_data}"
        )
        raise ValueError("Failed to exchange code for access token")

    return response_data["access_token"]


def link_linkedin_account(SECRET_GITHUB_user_id: str, auth_code: str) -> str:
    access_token = exchange_code_for_access_token(auth_code)
    # Here you would typically save the access token to your database, linked to the GitHub user ID
    # For example:
    # save_linkedin_access_token(SECRET_GITHUB_user_id, access_token)
    return access_token
