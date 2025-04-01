import pytest
import requests_mock
from types import SimpleNamespace
from backend.services.post_to_linkedin import post_to_linkedin
from types import SimpleNamespace


@pytest.mark.parametrize("linkedin_id, expected_urn", [
    ("123456", "urn:li:person:123456"),
    ("urn:li:person:123456", "urn:li:person:123456")
])
def test_post_to_linkedin_formats_author_correctly(monkeypatch, linkedin_id, expected_urn):
    user = SimpleNamespace(linkedin_token="fake-token", linkedin_id=linkedin_id)

    def mock_post(url, json, headers):
        assert json["author"] == expected_urn
        return SimpleNamespace(status_code=201, json=lambda: {"id": "fake-post-id"})

    monkeypatch.setattr("backend.services.post_to_linkedin.requests.post", mock_post)

    response = post_to_linkedin(user, "repo/example", "Fixed a bug")
    assert response.status_code == 201




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

        # ✅ Add this
        request_payload = m.request_history[0].json()
        assert request_payload["author"] == "urn:li:person:123456789", "Author URN should use 'person', not 'member'"

        assert result.status_code == 201
        assert result.json()["id"] == "mock_post_id"


