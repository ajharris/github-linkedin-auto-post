import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")
LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_to_linkedin(repo_name, commit_message):
    """
    Sends a post to LinkedIn with commit information.
    Returns the requests.Response object.
    """
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_USER_ID:
        raise ValueError("Missing LinkedIn credentials in environment variables")

    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    post_data = {
        "author": f"urn:li:person:{LINKEDIN_USER_ID}",
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
