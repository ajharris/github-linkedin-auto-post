import json
import pytest
from backend.models import GitHubEvent, User
from unittest.mock import patch


@pytest.mark.usefixtures("patch_signature_verification")
@patch("backend.services.post_to_linkedin.requests.post")
def test_webhook_push_event(mock_post, test_client):
    """Test that a valid push event is stored in the database."""
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": "linkedin_post_123"}

    user = User(github_id="testuser", github_token="fake_github_token", linkedin_token="fake_token", linkedin_id="123456789")
    from backend.models import db
    db.session.add(user)
    db.session.commit()

    payload = {
        "repository": {"full_name": "testuser/test-repo", "owner": {"id": "testuser"}},
        "pusher": {"name": "testuser"},
        "head_commit": {
            "message": "Fix bug in webhook handler",
            "url": "http://github.com/testuser/commit/123"
        },
    }

    response = test_client.post(
        "/webhook/github",
        data=json.dumps(payload),
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": "fake"
        },
    )

    assert response.status_code == 200, response.data
    assert GitHubEvent.query.count() == 1

    event = GitHubEvent.query.first()
    assert event.repo_name == "testuser/test-repo"
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
    assert response.status_code == 403  # signature should be invalid without patching


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


@pytest.mark.usefixtures("patch_signature_verification")
@patch("backend.services.post_to_linkedin.requests.post")
def test_webhook_links_event_to_correct_user(mock_post, test_client):
    """Test that a webhook event is linked to the correct user in the database."""
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": "linkedin_post_456"}

    user = User(github_id="otheruser", github_token="fake_github_token", linkedin_token="fake_token", linkedin_id="123456789")
    from backend.models import db
    db.session.add(user)
    db.session.commit()

    payload = {
        "repository": {"full_name": "otheruser/some-repo", "owner": {"id": "otheruser"}},
        "pusher": {"name": "otheruser"},
        "head_commit": {
            "message": "Refactor API endpoints",
            "url": "http://github.com/otheruser/commit/456"
        },
    }

    response = test_client.post(
        "/webhook/github",
        data=json.dumps(payload),
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": "fake"
        },
    )

    assert response.status_code == 200
    event = GitHubEvent.query.first()
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
