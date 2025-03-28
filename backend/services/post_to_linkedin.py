import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_ACCESS_TOKEN = None
LINKEDIN_USER_ID = None


import logging

def post_to_linkedin(repo_name, commit_message):
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    user_id = os.getenv("LINKEDIN_USER_ID")

    logging.info(f"[LinkedIn] Access token present: {bool(access_token)}")
    logging.info(f"[LinkedIn] User ID: {user_id}")

    if not access_token or not user_id:
        raise ValueError("Missing LinkedIn credentials in environment variables")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    post_data = {
    "author": f"urn:li:member:{user_id}",  # <-- this is the fix
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": f"🚀 Just pushed new code to {repo_name}!\n\n"
                        f"💬 {commit_message}\n\n"
                        "#buildinpublic #opensource"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}
    
    response = requests.post(LINKEDIN_POST_URL, json=post_data, headers=headers)
    return response
