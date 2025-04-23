import json
import os
import hmac
import hashlib
from unittest.mock import patch, MagicMock
from backend.models import GitHubEvent, User, db


def generate_signature(payload):
    """Generate a valid GitHub signature for the payload."""
    secret = os.getenv("SECRET_GITHUB_SECRET", "fake_secret").encode()
    body = json.dumps(payload).encode()
    return "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()


@patch(
    "backend.routes.post_to_linkedin",
    return_value=MagicMock(status_code=201, json=lambda: {"id": "test-post-id"}),
)
@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=True)
def test_SECRET_GITHUB_webhook(mock_verify, mock_post, client):
    """Test webhook processing a valid push event"""

    # Add test user to DB
    with client.application.app_context():
        user = User(
            SECRET_GITHUB_id="ajharris",
            SECRET_GITHUB_TOKEN="gh_token",
            linkedin_token="li_token",
        )
        db.session.add(user)
        db.session.commit()

    # Simulate GitHub push payload
    payload = {
        "pusher": {"name": "ajharris"},
        "repository": {
            "name": "github-linkedin-auto-post",
            "owner": {"id": "ajharris"},
        },
        "head_commit": {
            "message": "Test commit",
            "url": "https://github.com/ajharris/test/commit/abc123",
        },
    }

    secret = os.getenv("SECRET_GITHUB_SECRET", "fake_secret").encode()
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push",  # Added missing event type header
        "Content-Type": "application/json",
    }

    response = client.post("/webhook/github", data=body, headers=headers)

    assert response.status_code == 200, response.data
    assert response.get_json()["status"] == "success"


@patch(
    "backend.routes.post_to_linkedin",
    return_value=MagicMock(status_code=201, json=lambda: {"id": "linkedin_post_456"}),
)
@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=True)
def test_webhook_links_event_to_correct_user(
    mock_verify, mock_post_to_linkedin, test_client
):
    """Test that a webhook event is linked to the correct user in the database."""

    user = User(
        SECRET_GITHUB_id="otheruser",
        SECRET_GITHUB_TOKEN="fake_SECRET_GITHUB_TOKEN",
        linkedin_token="fake_token",
        linkedin_id="123456789",
    )
    with test_client.application.app_context():
        db.session.add(user)
        db.session.commit()

    payload = {
        "repository": {"name": "some-repo", "owner": {"id": "otheruser"}},
        "pusher": {"name": "otheruser"},
        "head_commit": {
            "message": "Refactor API endpoints",
            "url": "http://github.com/otheruser/commit/456",
        },
    }

    body = json.dumps(payload).encode()
    signature = generate_signature(payload)

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push",
        "Content-Type": "application/json",
    }

    response = test_client.post("/webhook/github", data=body, headers=headers)

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"

    with test_client.application.app_context():
        event = GitHubEvent.query.filter_by(
            repo_name="some-repo", commit_message="Refactor API endpoints"
        ).first()
        assert event is not None
        assert event.linkedin_post_id == "linkedin_post_456"


@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=True)
def test_webhook_unsupported_event_type(mock_verify, test_client):
    """Test that unsupported event types are handled gracefully."""
    payload = {
        "repository": {"name": "test-repo", "owner": {"id": "testuser"}},
        "pusher": {"name": "testuser"},
        "head_commit": {
            "message": "Fix bug in webhook handler",
            "url": "http://github.com/testuser/commit/123",
        },
    }

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": generate_signature(payload),
        "Content-Type": "application/json",
    }

    response = test_client.post("/webhook/github", json=payload, headers=headers)
    assert response.status_code in [204, 400]
    assert (
        "Unsupported event type" in response.get_data(as_text=True)
        or response.status_code == 204
    )


def test_webhook_invalid_payload(test_client):
    """Test that malformed JSON is rejected."""
    response = test_client.post(
        "/webhook/github",
        data="invalid json",
        content_type="application/json",
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": "fake"},
    )
    assert response.status_code == 403


def test_webhook_unauthorized_request(test_client):
    """Test that requests without GitHub signature header are rejected."""
    response = test_client.post(
        "/webhook/github",
        data=json.dumps({"repository": {"full_name": "testuser/test-repo"}}),
        content_type="application/json",
        headers={"X-GitHub-Event": "push"},
    )
    assert response.status_code == 403


def test_webhook_route_exists(test_client):
    """This test fails if the GitHub webhook route is missing or returns wrong status."""
    response = test_client.post(
        "/webhook/github",
        data="{}",
        content_type="application/json",
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": "fake"},
    )
    assert response.status_code != 404
    assert response.status_code == 403


@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=True)
def test_webhook_redundant_event(mock_verify, test_client):

    # Add test user to DB
    with test_client.application.app_context():
        user = User(
            SECRET_GITHUB_id="testuser",
            SECRET_GITHUB_TOKEN="fake_SECRET_GITHUB_TOKEN",
            linkedin_token="fake_token",
            linkedin_id="123456789",
        )
        db.session.add(user)
        db.session.commit()

    # Refresh the user instance to ensure it is attached to the session
    with test_client.application.app_context():
        user = db.session.merge(user)
        db.session.refresh(user)

    # Add a redundant event to the database
    with test_client.application.app_context():
        redundant_event = GitHubEvent(
            user_id=user.id,
            repo_name="test-repo",
            commit_message="Fix bug in webhook handler",
            commit_url="http://github.com/testuser/commit/123",
            linkedin_post_id="mock_post_id",
        )
        db.session.add(redundant_event)
        db.session.commit()

    # Ensure the redundant event exists
    with test_client.application.app_context():
        assert (
            GitHubEvent.query.filter_by(
                user_id=user.id,
                repo_name="test-repo",
                commit_message="Fix bug in webhook handler",
            ).first()
            is not None
        )

    payload = {
        "repository": {"name": "test-repo", "owner": {"id": "testuser"}},
        "pusher": {"name": "testuser"},
        "head_commit": {
            "message": "Fix bug in webhook handler",
            "url": "http://github.com/testuser/commit/123",
        },
    }

    headers = {
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": generate_signature(payload),
        "Content-Type": "application/json",
    }

    with patch("backend.routes.post_to_linkedin") as mock_post_to_linkedin:
        mock_post_to_linkedin.return_value = MagicMock(
            status_code=200, json=lambda: {"id": "mock_post_id"}
        )  # Simulate valid response

        response = test_client.post("/webhook/github", json=payload, headers=headers)

        assert response.status_code == 200
        mock_post_to_linkedin.assert_not_called()


@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=True)
def test_webhook_pull_request_event(mock_verify, test_client):
    """Test that pull request events are parsed correctly."""
    payload = {
        "action": "opened",
        "pull_request": {
            "title": "Add new feature",
            "html_url": "http://github.com/testuser/repo/pull/1",
            "user": {"login": "testuser"},
        },
        "repository": {"name": "test-repo", "owner": {"id": "testuser"}},
    }

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": generate_signature(payload),
        "Content-Type": "application/json",
    }

    response = test_client.post("/webhook/github", json=payload, headers=headers)

    assert response.status_code in [204, 400]
    assert (
        "Pull request event received" in response.get_data(as_text=True)
        or response.status_code == 204
    )


@patch("backend.routes.verify_SECRET_GITHUB_signature", return_value=False)
def test_webhook_invalid_signature(mock_verify, test_client):
    """Test that payloads with invalid signatures are rejected."""
    payload = {
        "repository": {"name": "test-repo", "owner": {"id": "testuser"}},
        "pusher": {"name": "testuser"},
        "head_commit": {
            "message": "Fix bug in webhook handler",
            "url": "http://github.com/testuser/commit/123",
        },
    }

    headers = {
        "X-GitHub-Event": "push",
        "X-Hub-Signature-256": "invalid_signature",
        "Content-Type": "application/json",
    }

    response = test_client.post("/webhook/github", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.get_json()["error"] == "Unauthorized"
