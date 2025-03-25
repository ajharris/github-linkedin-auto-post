import json
import pytest
from backend.app import create_app, db
from backend.models import GitHubEvent, User
from unittest.mock import patch

@pytest.fixture
def test_client():
    """Set up test client and database."""
    app = create_app("testing")
    client = app.test_client()
    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

@patch("backend.routes.verify_github_signature", return_value=True)
def test_webhook_push_event(mock_verify, test_client):
    """Test that a valid push event is stored in the database."""
    user = User(github_id="testuser", github_token="fake_github_token", linkedin_token="fake_token")
    db.session.add(user)
    db.session.commit()

    payload = {
        "repository": {"full_name": "testuser/test-repo"},
        "pusher": {"name": "testuser"},
        "head_commit": {"message": "Fix bug in webhook handler", "url": "http://github.com/testuser/commit/123"},
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
    assert GitHubEvent.query.count() == 1

    event = GitHubEvent.query.first()
    assert event.repo_name == "testuser/test-repo"
    assert event.commit_message == "Fix bug in webhook handler"
    assert event.user.github_id == "testuser"

@patch("backend.routes.verify_github_signature", return_value=True)
def test_webhook_invalid_payload(mock_verify, test_client):
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
    assert response.status_code == 400

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
def test_webhook_links_event_to_correct_user(mock_verify, test_client):
    """Test that a webhook event is linked to the correct user in the database."""
    user = User(github_id="otheruser", github_token="fake_github_token", linkedin_token="fake_token")
    db.session.add(user)
    db.session.commit()

    payload = {
        "repository": {"full_name": "otheruser/some-repo"},
        "pusher": {"name": "otheruser"},
        "head_commit": {"message": "Refactor API endpoints", "url": "http://github.com/otheruser/commit/456"},
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
