import os
import pytest
import requests
import requests_mock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Mock LinkedIn API URL
LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def post_to_linkedin(repo, message):
    """
    Function to post a commit update to LinkedIn.
    """
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    post_data = {
        "author": "urn:li:person:YOUR_LINKEDIN_USER_ID",  # Replace with your LinkedIn User ID
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": f"🚀 New commit in {repo}: {message}"},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(LINKEDIN_POST_URL, json=post_data, headers=headers)
    return response


def test_post_to_linkedin_success(requests_mock):
    """
    Test successful LinkedIn post using a mocked API response.
    """
    mock_response = {"id": "urn:li:ugcPost:123456789"}
    
    # Mock the LinkedIn API call
    requests_mock.post(LINKEDIN_POST_URL, json=mock_response, status_code=201)

    # Run the function
    response = post_to_linkedin("TestRepo", "Initial commit.")

    # Assertions
    assert response.status_code == 201
    assert response.json() == mock_response


def test_post_to_linkedin_auth_failure(requests_mock):
    """
    Test LinkedIn API failure due to authentication issues.
    """
    mock_response = {"message": "Invalid access token", "status": 401}
    
    # Mock the LinkedIn API call to return an authentication error
    requests_mock.post(LINKEDIN_POST_URL, json=mock_response, status_code=401)

    # Run the function
    response = post_to_linkedin("TestRepo", "Initial commit.")

    # Assertions
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid access token"
