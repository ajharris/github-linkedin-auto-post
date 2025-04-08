import os
from flask import current_app, json, jsonify
import requests
from dotenv import load_dotenv
import logging

from backend.models import User

load_dotenv()

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_to_linkedin(user, repo_name, commit_message):
    if not user:
        current_app.logger.warning(f"[post_to_linkedin] No user provided.")
        user = User.query.first()
        if not user:
            raise ValueError("User not found")
        current_app.logger.warning(f"[Webhook] Fallback user: {getattr(user, 'github_id', 'None')}")

    access_token = user.linkedin_token
    user_id = user.linkedin_id

    logging.info(f"[LinkedIn] User ID: {user_id}")

    if not access_token or not user_id:
        raise ValueError("Missing LinkedIn credentials")

    # Ensure the user_id is properly formatted
    if not user_id.startswith("urn:li:person:"):
        user_id = f"urn:li:person:{user_id}"  # Correct the format if necessary

    author_urn = user_id

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"New update from {repo_name}: {commit_message}"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(LINKEDIN_POST_URL, headers=headers, json=payload)

    if response.status_code != 201:
        current_app.logger.error(f"[LinkedIn] Failed to post: {response.status_code} {response.text}")
        raise ValueError(f"Failed to post to LinkedIn: {response.status_code} {response.text}")

    current_app.logger.info(f"[LinkedIn] Successfully posted to LinkedIn for user {user.github_id}")
    return response.json()
