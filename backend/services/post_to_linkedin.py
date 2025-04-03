import os
from flask import current_app, json
import requests
from dotenv import load_dotenv
import logging

from backend.models import User

load_dotenv()

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_to_linkedin(user, repo_name, commit_message):
    if not user:
        current_app.logger.warning(f"[Webhook] No user found for GitHub ID {github_user_id}")
        user = User.query.first()
        current_app.logger.warning(f"[Webhook] Fallback: using first user {user.github_id}")

    
    access_token = user.linkedin_token
    user_id = user.linkedin_id

    
    logging.info(f"[LinkedIn] User ID: {user_id}")

    if not access_token or not user_id:
        raise ValueError("Missing LinkedIn credentials")

    # Ensure the user_id is properly formatted
    if not user_id.startswith("urn:li:member:"):
        author_urn = f"urn:li:member:{user_id}"

    else:
        author_urn = user_id

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"\ud83d\ude80 Just pushed new code to {repo_name}!\n\n"
                            f"\ud83d\udcac {commit_message}\n\n"
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

    current_app.logger.info(f"[LinkedIn] Posting as {user.linkedin_id}")
    current_app.logger.info(f"[LinkedIn] Payload: {json.dumps(post_data, indent=2)}")
    current_app.logger.info(f"[LinkedIn] Response: {response.status_code} {response.text}")


    return response
