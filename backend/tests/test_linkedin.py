import os
import pytest
import requests
import requests_mock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")

# Mock LinkedIn API URL
LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def test_linkedin_env_vars_set():
    assert os.getenv("LINKEDIN_ACCESS_TOKEN"), "Missing LINKEDIN_ACCESS_TOKEN"
    assert os.getenv("LINKEDIN_USER_ID"), "Missing LINKEDIN_USER_ID"


def post_to_linkedin(repo, message):
    """
    Function to post a commit update to LinkedIn.
    """
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    post_data = {
        "author": "urn:li:person:{LINKEDIN_USER_ID}",  # Replace with your LinkedIn User ID
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


def test_post_to_linkedin_success():
    # Create a fake user with valid credentials
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")

    with requests_mock.Mocker() as m:
        m.post("https://api.linkedin.com/v2/ugcPosts", json={"id": "mock_post_id"}, status_code=201)

        result = post_to_linkedin(user, "ajharris/github-linkedin-auto-post", "Commit message")

        # ✅ Add this
        request_payload = m.request_history[0].json()
        assert request_payload["author"] == "urn:li:person:123456789", "Author URN should use 'person', not 'member'"

        assert result.status_code == 201
        assert result.json()["id"] == "mock_post_id"



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

def test_post_to_linkedin_server_error(requests_mock):
    """
    Test LinkedIn API server error.
    """
    mock_response = {"message": "Internal Server Error"}
    requests_mock.post(LINKEDIN_POST_URL, json=mock_response, status_code=500)

    response = post_to_linkedin("TestRepo", "Something broke.")
    
    assert response.status_code == 500
    assert response.json()["message"] == "Internal Server Error"

def test_post_payload_format(requests_mock):
    """
    Ensure the outgoing post data is formatted correctly.
    """
    requests_mock.post(LINKEDIN_POST_URL, json={"id": "test"}, status_code=201)

    repo = "MyRepo"
    message = "Did a thing."
    post_to_linkedin(repo, message)

    last_request = requests_mock.last_request
    payload = last_request.json()
    
    assert payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"] == f"🚀 New commit in {repo}: {message}"
    assert payload["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"] == "PUBLIC"

