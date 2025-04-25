import os
from flask import current_app, json
import requests
from dotenv import load_dotenv
import logging
import time

from backend.models import User, db
from backend.services.post_generator import generate_post_from_webhook
from backend.services.linkedin_oauth import exchange_code_for_access_token
from backend.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"


def post_to_linkedin(user, repo_name, commit_message, webhook_payload):
    if not user:
        current_app.logger.warning("[post_to_linkedin] No user provided.")
        user = User.query.first()
        if not user:
            response = requests.Response()
            response.status_code = 404
            response._content = b"User not found"
            return response
        current_app.logger.warning(
            f"[Webhook] Fallback user: {getattr(user, 'SECRET_GITHUB_id', 'None')}"
        )

    access_token = user.linkedin_token
    user_id = user.linkedin_id

    logging.info(f"[LinkedIn] User ID: {user_id}")

    if not access_token or not user_id:
        response = requests.Response()
        response.status_code = 400
        response._content = b"Missing LinkedIn credentials"
        return response

    if not user_id.startswith("urn:li:"):
        user_id = f"urn:li:member:{user_id}"

    author_urn = user_id

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    post_text = generate_post_from_webhook(webhook_payload)

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    response = requests.post(LINKEDIN_POST_URL, headers=headers, json=payload)

    if response.status_code == 401:
        current_app.logger.error(f"[LinkedIn] Authentication failed: {response.text}")
        raise ValueError(f"Failed to post to LinkedIn: {response.status_code}")
    elif response.status_code >= 500:
        current_app.logger.error(f"[LinkedIn] Server error: {response.text}")
        raise ValueError(f"Failed to post to LinkedIn: {response.status_code}")
    elif response.status_code not in {201, 401} and response.status_code < 500:
        current_app.logger.error(
            f"[LinkedIn] Unexpected error: {response.status_code} {response.text}"
        )

    return response


def send_post_to_linkedin(
    user, repo_name, commit_message, webhook_payload, retries=3, delay=2
):
    """
    Sends a post to LinkedIn using the user's credentials with retry logic.

    Args:
        user (User): The user object containing LinkedIn credentials.
        repo_name (str): The name of the repository.
        commit_message (str): The commit message.
        webhook_payload (dict): The webhook payload from GitHub.
        retries (int): Number of retry attempts in case of failure.
        delay (int): Delay in seconds between retries.

    Returns:
        Response: The response from the LinkedIn API.
    """
    if not user.linkedin_token:
        logging.warning("[LinkedIn] Missing LinkedIn token. Attempting to refresh.")
        try:
            user.linkedin_token = exchange_code_for_access_token(
                user.SECRET_GITHUB_TOKEN
            )
            db.session.commit()
        except Exception as e:
            logging.error(f"[LinkedIn] Failed to refresh token: {e}")
            raise

    for attempt in range(retries):
        try:
            response = post_to_linkedin(
                user, repo_name, commit_message, webhook_payload
            )
            if response.status_code == 201:
                logging.info(f"[LinkedIn] Post successful: {response.json()}")
                return response
            else:
                logging.error(
                    f"[LinkedIn] Post failed: {response.status_code} {response.text}"
                )
                return response
        except Exception as e:
            logging.error(
                f"[LinkedIn] Exception during post (attempt {attempt + 1}): {e}"
            )
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise
