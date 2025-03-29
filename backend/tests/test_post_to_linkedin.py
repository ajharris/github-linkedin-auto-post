import pytest
import requests_mock
from types import SimpleNamespace
from backend.services.post_to_linkedin import post_to_linkedin


def test_post_to_linkedin_missing_env(monkeypatch):
    # Clear any fallback env vars just in case
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)

    # Fake user with missing fields
    user = SimpleNamespace(linkedin_token=None, linkedin_id=None)

    with pytest.raises(ValueError, match="Missing LinkedIn credentials"):
        post_to_linkedin(user, "ajharris/github-linkedin-auto-post", "This is a commit")


def test_post_to_linkedin_success():
    # Create a fake user with valid credentials
    user = SimpleNamespace(linkedin_token="fake_token", linkedin_id="123456789")

    with requests_mock.Mocker() as m:
        m.post("https://api.linkedin.com/v2/ugcPosts", json={"id": "mock_post_id"}, status_code=201)

        result = post_to_linkedin(user, "ajharris/github-linkedin-auto-post", "Commit message")
        assert result.status_code == 201
        assert result.json()["id"] == "mock_post_id"
