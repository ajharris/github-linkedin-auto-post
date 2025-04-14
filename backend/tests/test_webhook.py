import json
import pytest
from backend.models import GitHubEvent, User, db
from unittest.mock import patch, MagicMock
import os
import hmac
import hashlib


@patch("backend.routes.verify_github_signature", return_value=True)
@patch("backend.routes.post_to_linkedin")
def test_webhook_push_event(mock_post_to_linkedin, mock_verify_signature, test_client):
    """Test that a valid push event is stored in the database."""
    mock_post_to_linkedin.side_effect = lambda *args, **kwargs: MagicMock(
    status_code=201,
    json=lambda: {"id": "linkedin_post_123"}  # or ...456 depending on test
)


    user = User(github_id="testuser", github_token="fake_github_token", linkedin_token="fake_token", linkedin_id="123456789")
    with test_client.application.app_context():
        db.session.add(user)
        db.session.commit()

    payload = {
        "repository": {"name": "test-repo", "owner": {"id": "testuser"}},
        "pusher": {"name": "testuser"},
        "head_commit": {
            "message": "Fix bug in webhook handler",
            "url": "http://github.com/testuser/commit/123"
        },
    }

    secret = os.getenv("GITHUB_SECRET", "fake_secret").encode()
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }

    response = test_client.post("/webhook/github", data=body, headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"status": "success", "linkedin_post_id": "linkedin_post_123"}
    assert GitHubEvent.query.count() == 1

    event = GitHubEvent.query.first()
    assert event.repo_name == "test-repo"
    assert event.commit_message == "Fix bug in webhook handler"
    assert event.user.github_id == "testuser"


def test_webhook_invalid_payload(test_client):
    """Test that malformed JSON is rejected."""
    response = test_client.post(
        "/webhook/github",
        data="invalid json",
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": "fake"
        },
    )
    assert response.status_code == 403


def test_webhook_unauthorized_request(test_client):
    """Test that requests without GitHub signature header are rejected."""
    response = test_client.post(
        "/webhook/github",
        data=json.dumps({"repository": {"full_name": "testuser/test-repo"}}),
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push"
        }
    )
    assert response.status_code == 403

@patch("backend.routes.verify_github_signature", return_value=True)
@patch("backend.routes.post_to_linkedin")
def test_webhook_links_event_to_correct_user(mock_post_to_linkedin, mock_verify_signature, test_client):
    """Test that a webhook event is linked to the correct user in the database."""
    # Correctly mock the function to handle all four arguments
    mock_post_to_linkedin.side_effect = lambda *args, **kwargs: MagicMock(
        status_code=201,
        json=lambda: {"id": "linkedin_post_456"} 
    )


    user = User(github_id="otheruser", github_token="fake_github_token", linkedin_token="fake_token", linkedin_id="123456789")
    with test_client.application.app_context():
        db.session.add(user)
        db.session.commit()

    payload = {
        "repository": {"name": "some-repo", "owner": {"id": "otheruser"}},
        "pusher": {"name": "otheruser"},
        "head_commit": {
            "message": "Refactor API endpoints",
            "url": "http://github.com/otheruser/commit/456"
        },
    }

    secret = os.getenv("GITHUB_SECRET", "fake_secret").encode()
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }

    response = test_client.post("/webhook/github", data=body, headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"status": "success", "linkedin_post_id": "linkedin_post_456"}
    assert GitHubEvent.query.count() == 1

    event = GitHubEvent.query.first()
    assert event.repo_name == "some-repo"
    assert event.commit_message == "Refactor API endpoints"
    assert event.user.github_id == "otheruser"


def test_webhook_route_exists(test_client):
    """This test fails if the GitHub webhook route is missing or returns wrong status."""
    response = test_client.post(
        "/webhook/github",
        data="{}",
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": "fake"
        }
    )
    assert response.status_code != 404, "Webhook route not found (404)"
    assert response.status_code == 403, f"Expected forbidden due to invalid signature, got {response.status_code}"
