import os
import pytest
from backend.services.post_to_linkedin import post_to_linkedin

def test_post_to_linkedin_missing_env(monkeypatch):
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)

    with pytest.raises(ValueError, match="Missing LinkedIn credentials"):
        post_to_linkedin("ajharris/github-linkedin-auto-post", "This is a commit")

import requests_mock

def test_post_to_linkedin_success(monkeypatch):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "fake_token")
    monkeypatch.setenv("LINKEDIN_USER_ID", "urn:li:person:testuser")

    with requests_mock.Mocker() as m:
        m.post("https://api.linkedin.com/v2/ugcPosts", json={"id": "mock_post_id"}, status_code=201)

        result = post_to_linkedin("ajharris/github-linkedin-auto-post", "Commit message")
        assert result.json()["id"] == "mock_post_id"


