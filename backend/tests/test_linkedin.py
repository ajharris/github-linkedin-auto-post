import os
import pytest
import requests_mock
from types import SimpleNamespace
from dotenv import load_dotenv

from backend.services.post_to_linkedin import post_to_linkedin

# Load environment variables for the env var test
load_dotenv()

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"

def test_linkedin_env_vars_set():
    assert os.getenv("LINKEDIN_ACCESS_TOKEN"), "Missing LINKEDIN_ACCESS_TOKEN"
    assert os.getenv("LINKEDIN_USER_ID"), "Missing LINKEDIN_USER_ID"


def test_post_to_linkedin_success():
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json={"id": "mock_post_id"}, status_code=201)

        result = post_to_linkedin(user, "ajharris/github-linkedin-auto-post", "Commit message")

        request_payload = m.request_history[0].json()
        assert request_payload["author"] == "urn:li:person:123456789"
        assert result.status_code == 201
        assert result.json()["id"] == "mock_post_id"


def test_post_to_linkedin_auth_failure():
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")
    mock_response = {"message": "Invalid access token", "status": 401}

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json=mock_response, status_code=401)
        response = post_to_linkedin(user, "TestRepo", "Initial commit.")

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid access token"


def test_post_to_linkedin_server_error():
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")
    mock_response = {"message": "Internal Server Error"}

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json=mock_response, status_code=500)
        response = post_to_linkedin(user, "TestRepo", "Something broke.")

    assert response.status_code == 500
    assert response.json()["message"] == "Internal Server Error"


def test_post_payload_format():
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")
    repo = "MyRepo"
    message = "Did a thing."

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json={"id": "test"}, status_code=201)
        post_to_linkedin(user, repo, message)

        payload = m.last_request.json()

        expected_text = f"🚀 Just pushed new code to {repo}!\n\n💬 {message}\n\n#buildinpublic #opensource"
        actual_text = payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]

        assert actual_text == expected_text
        assert payload["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"] == "PUBLIC"
        assert payload["author"] == "urn:li:person:123456789"
