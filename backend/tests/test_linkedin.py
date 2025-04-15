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
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id="123456789"
    )
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json={"id": "mock_post_id"}, status_code=201)
        result = post_to_linkedin(user, "test-repo", "Initial commit", webhook_payload)
        assert result.status_code == 201


def test_post_to_linkedin_auth_failure():
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id="123456789"
    )
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }
    mock_response = {"message": "Invalid access token", "status": 401}

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json=mock_response, status_code=401)
        with pytest.raises(ValueError, match="Failed to post to LinkedIn: 401"):
            post_to_linkedin(user, "test-repo", "Initial commit", webhook_payload)


def test_post_to_linkedin_server_error():
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id="123456789"
    )
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }
    mock_response = {"message": "Internal Server Error"}

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json=mock_response, status_code=500)
        with pytest.raises(ValueError, match="Failed to post to LinkedIn: 500"):
            post_to_linkedin(user, "test-repo", "Initial commit", webhook_payload)


def test_post_payload_format():
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id="123456789"
    )
    repo = "test-repo"
    message = "Initial commit"
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }

    with requests_mock.Mocker() as m:
        m.post(LINKEDIN_POST_URL, json={"id": "test"}, status_code=201)
        post_to_linkedin(user, repo, message, webhook_payload)
        payload = m.last_request.json()

        expected_text = (
            "🚀 Test User just pushed to test-repo!\n\n"
            "💬 Commit message: \"Initial commit\"\n\n"
            "🔗 Check it out: https://github.com/test-repo\n\n"
            "#buildinpublic #opensource"
        )
        actual_text = payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]

        assert actual_text == expected_text
        assert payload["visibility"]["com.linkedin.ugc.MemberNetworkVisibility"] == "PUBLIC"
        assert payload["author"] == "urn:li:member:123456789"
