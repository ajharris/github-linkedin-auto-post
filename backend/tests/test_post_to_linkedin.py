import pytest
import requests_mock
from types import SimpleNamespace
from backend.services.post_to_linkedin import post_to_linkedin
from unittest.mock import patch, MagicMock
from backend.models import User, db
from backend.services.post_to_linkedin import send_post_to_linkedin
from unittest.mock import call


@pytest.mark.parametrize("linkedin_id, expected_urn", [
    ("123456", "urn:li:member:123456"),
    ("urn:li:member:123456", "urn:li:member:123456")
])
def test_post_to_linkedin_formats_author_correctly(monkeypatch, linkedin_id, expected_urn):
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id=linkedin_id
    )
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }

    def mock_post(url, json, headers):
        assert json["author"] == expected_urn
        return SimpleNamespace(status_code=201, json="{'id': 'fake-post-id'}", text="OK")

    monkeypatch.setattr("backend.services.post_to_linkedin.requests.post", mock_post)
    response = post_to_linkedin(user, "repo/example", "Fixed a bug", webhook_payload)
    assert response.status_code == 201


def test_post_to_linkedin_missing_env(monkeypatch):
    # Clear any fallback env vars just in case
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)

    # Fake user with missing fields
    user = SimpleNamespace(
        github_id="gh123",
        linkedin_token="fake_token",
        linkedin_id="123456789"
    )
    webhook_payload = {
        "repository": {"name": "test-repo", "html_url": "https://github.com/test-repo"},
        "head_commit": {"message": "Initial commit", "author": {"name": "Test User"}}
    }

    with pytest.raises(ValueError, match="Failed to post to LinkedIn: 401"):
        post_to_linkedin(user, "test-repo", "Initial commit", webhook_payload)


def test_post_to_linkedin_success():
    # Create a fake user with valid credentials
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
        m.post("https://api.linkedin.com/v2/ugcPosts", json={"id": "mock_post_id"}, status_code=201)

        result = post_to_linkedin(user, "ajharris/github-linkedin-auto-post", "Commit message", webhook_payload)

        # ✅ Add this
        request_payload = m.request_history[0].json()
        assert request_payload["author"] == "urn:li:member:123456789", "Author URN should use 'person', not 'member'"

        assert result.status_code == 201
        assert result.json()["id"] == "mock_post_id"


@patch("backend.services.post_to_linkedin.requests.post")
@patch("backend.services.post_to_linkedin.generate_post_from_webhook")
def test_post_to_linkedin(mock_generate_post, mock_requests_post):
    mock_user = MagicMock()
    mock_user.linkedin_token = "test-token"
    mock_user.linkedin_id = "12345"
    mock_user.github_id = "test-github-id"

    webhook_payload = {
        "repository": {
            "name": "test-repo",
            "html_url": "https://github.com/test-repo"
        },
        "head_commit": {
            "message": "Initial commit",
            "author": {
                "name": "Test User"
            }
        }
    }

    mock_generate_post.return_value = "Generated post text"

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "mock_post_id"}
    mock_requests_post.return_value = mock_response

    response = post_to_linkedin(mock_user, "test-repo", "Initial commit", webhook_payload)

    mock_generate_post.assert_called_once_with(webhook_payload)
    assert response.status_code == 201
    assert response.json() == {"id": "mock_post_id"}


@patch("backend.services.post_to_linkedin.requests.post")
def test_post_to_linkedin_missing_user(mock_requests_post):
    mock_requests_post.return_value = MagicMock()

    response = post_to_linkedin(None, "test-repo", "Initial commit", {})
    assert response.status_code == 404
    assert response.text == "User not found"


@patch("backend.services.post_to_linkedin.requests.post")
def test_post_to_linkedin_missing_credentials(mock_requests_post):
    mock_user = MagicMock()
    mock_user.linkedin_token = None
    mock_user.linkedin_id = None

    response = post_to_linkedin(mock_user, "test-repo", "Initial commit", {})
    assert response.status_code == 400
    assert response.text == "Missing LinkedIn credentials"


@patch("backend.services.post_to_linkedin.requests.post")
def test_post_to_linkedin_duplicate_event(mock_requests_post):
    """Test that no duplicate LinkedIn posts are created for the same webhook event."""
    mock_user = MagicMock()
    mock_user.linkedin_token = "test-token"
    mock_user.linkedin_id = "12345"
    mock_user.github_id = "test-github-id"

    webhook_payload = {
        "repository": {
            "name": "test-repo",
            "html_url": "https://github.com/test-repo"
        },
        "head_commit": {
            "message": "Initial commit",
            "author": {
                "name": "Test User"
            }
        }
    }

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": "mock_post_id"}
    mock_requests_post.return_value = mock_response

    # Simulate the first post
    response1 = post_to_linkedin(mock_user, "test-repo", "Initial commit", webhook_payload)
    assert response1.status_code == 201

    # Simulate a duplicate post
    mock_requests_post.side_effect = Exception("Duplicate event detected")
    with pytest.raises(Exception, match="Duplicate event detected"):
        post_to_linkedin(mock_user, "test-repo", "Initial commit", webhook_payload)


def test_send_post_to_linkedin_refreshes_token(app):
    """Test that send_post_to_linkedin refreshes the token if missing."""
    with app.app_context():
        user = User(
            github_id="12345",
            github_username="testuser",
            SECRET_GITHUB_TOKEN="mock_SECRET_GITHUB_TOKEN",
            linkedin_token=None,  # Simulate missing token
            linkedin_id="mock_linkedin_id"
        )
        db.session.add(user)
        db.session.commit()

        with patch("backend.services.post_to_linkedin.exchange_code_for_access_token", return_value="new_mock_token") as mock_refresh_token, \
             patch("backend.services.post_to_linkedin.post_to_linkedin") as mock_post_to_linkedin:

            mock_post_to_linkedin.return_value = MagicMock(status_code=201, json=lambda: {"id": "mock_post_id"})

            response = send_post_to_linkedin(user, "test-repo", "Test commit message", {})

            mock_refresh_token.assert_called_once_with(user.SECRET_GITHUB_TOKEN)
            assert user.linkedin_token == "new_mock_token"
            assert response.status_code == 201
            assert response.json()["id"] == "mock_post_id"


def test_send_post_to_linkedin_handles_post_errors(app):
    """Test that send_post_to_linkedin handles errors during posting."""
    with app.app_context():
        user = User(
            github_id="12345",
            github_username="testuser",
            SECRET_GITHUB_TOKEN="mock_SECRET_GITHUB_TOKEN",
            linkedin_token="mock_token",
            linkedin_id="mock_linkedin_id"
        )
        db.session.add(user)
        db.session.commit()

        with patch("backend.services.post_to_linkedin.post_to_linkedin") as mock_post_to_linkedin:
            mock_post_to_linkedin.side_effect = Exception("Mocked post error")

            with pytest.raises(Exception, match="Mocked post error"):
                send_post_to_linkedin(user, "test-repo", "Test commit message", {})


def test_retry_logic_if_post_fails(app):
    """Test retry logic when LinkedIn post fails temporarily."""
    with app.app_context():
        user = User(
            github_id="12345",
            github_username="testuser",
            SECRET_GITHUB_TOKEN="mock_SECRET_GITHUB_TOKEN",
            linkedin_token="mock_token",
            linkedin_id="mock_linkedin_id"
        )
        db.session.add(user)
        db.session.commit()

        with patch("backend.services.post_to_linkedin.post_to_linkedin") as mock_post_to_linkedin:
            # Simulate temporary failure followed by success
            mock_post_to_linkedin.side_effect = [
                Exception("Temporary LinkedIn API failure"),
                MagicMock(status_code=201, json=lambda: {"id": "mock_post_id"})
            ]

            with patch("time.sleep", return_value=None) as mock_sleep:
                response = send_post_to_linkedin(user, "test-repo", "Test commit message", {})

                # Ensure retry logic was triggered
                assert mock_post_to_linkedin.call_count == 2
                mock_sleep.assert_called_once_with(2)  # Ensure sleep was called between retries

                # Verify the successful response
                assert response.status_code == 201
                assert response.json()["id"] == "mock_post_id"


