import os
from dotenv import load_dotenv
import logging

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
REDIRECT_URI = "https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin/callback"

def build_linkedin_auth_url(github_user_id: str) -> str:
    if not CLIENT_ID:
        logging.error("[LinkedIn OAuth] CLIENT_ID is not set in environment variables.")
        raise ValueError("Missing LinkedIn CLIENT_ID")

    return (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=w_member_social"
        f"&state={github_user_id}"
    )
