import os
import json
import pytest
from unittest.mock import patch, MagicMock
import hmac
import hashlib
from backend.routes import routes
from backend.models import db, User
from backend.app import create_app

# Set test environment variables
os.environ["LINKEDIN_ACCESS_TOKEN"] = "test_token"
os.environ["LINKEDIN_USER_ID"] = "test_user_id"
os.environ["GITHUB_SECRET"] = "t4keth1s"


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_post():
    """Fixture for mocking post_to_linkedin."""
    with patch("backend.routes.post_to_linkedin") as mock:
        yield mock


def test_serve_index(client):
    """Test serving the frontend index file"""
    response = client.get("/")
    assert response.status_code in [200, 404]  # 404 if no frontend build exists


def test_linkedin_auth_redirect(client):
    """Test LinkedIn authentication redirect"""
    response = client.get("/auth/linkedin")
    assert response.status_code == 302
    assert "https://www.linkedin.com/oauth/v2/authorization" in response.location


from unittest.mock import patch

@patch("requests.get")
@patch("requests.post")
def test_linkedin_callback_success(mock_post, mock_get, client):
    """Test LinkedIn OAuth callback"""
    # Mock token exchange
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "test_token",
        "id_token": "mock_id_token"
    }

    # Mock profile fetch
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"sub": "123456789"}

    # Add fake GitHub user so the callback logic finds them
    with client.application.app_context():
        from backend.models import User, db
        user = User(github_id="test", github_token="fake-token")
        db.session.add(user)
        db.session.commit()

    # Call the callback
    response = client.get("/auth/linkedin/callback?code=valid_code&state=test")

    assert response.status_code == 200, response.data
    assert b"LinkedIn Access Token and ID stored successfully" in response.data


def test_linkedin_callback_no_code(client):
    """Test LinkedIn OAuth callback failure due to missing code"""
    response = client.get("/auth/linkedin/callback")
    assert response.status_code == 400
    assert "Authorization failed" in response.get_data(as_text=True)


def test_github_webhook_no_signature(client):
    """Test GitHub webhook request with missing signature."""
    response = client.post("/webhook/github", json={"test": "data"}, headers={"Content-Type": "application/json"})
    assert response.status_code == 403
    assert response.get_json() == {"error": "Invalid signature"}


@patch("backend.routes.post_to_linkedin", return_value=MagicMock(status_code=201, json=lambda: {"id": "test-post-id"}))
@patch("backend.routes.verify_github_signature", return_value=True)
def test_github_webhook(mock_verify, mock_post, client):
    """Test webhook processing a valid push event"""

    # Add test user to DB
    user = User(github_id="ajharris", github_token="gh_token", linkedin_token="li_token")
    db.session.add(user)
    db.session.commit()

    # Simulate GitHub push payload
    payload = {
        "pusher": {"name": "ajharris"},
        "repository": {"name": "github-linkedin-auto-post", "owner": {"id": "ajharris"}},
        "head_commit": {
            "message": "Test commit",
            "url": "https://github.com/ajharris/test/commit/abc123"
        }
    }

    secret = os.getenv("GITHUB_SECRET").encode()
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }

    response = client.post("/webhook/github", data=body, headers=headers)

    assert response.status_code == 200, response.data
    assert response.get_json() == {"status": "success", "linkedin_post_id": "test-post-id"}


def test_github_status_returns_user_info(client):
    """Test the /api/github/<github_id>/status route."""
    with client.application.app_context():
        user = User(
            github_id="123456",
            github_username="octocat",
            github_token="fake-token"
        )
        db.session.add(user)
        db.session.commit()

    response = client.get("/api/github/123456/status")
    assert response.status_code == 200
    assert response.get_json() == {
        "linked": False,
        "github_id": "123456",
        "github_username": "octocat",
        "linkedin_id": None
    }


from unittest.mock import patch, MagicMock
import hmac
import json
import os


@patch("backend.routes.verify_github_signature", return_value=True)
@patch("backend.routes.post_to_linkedin")
def test_webhook_push_event(mock_post_to_linkedin, mock_verify, client):
    mock_post_to_linkedin.side_effect = lambda *args, **kwargs: MagicMock(
        status_code=201,
        json=lambda: {"id": "linkedin_post_123"}
    )

    user = User(github_id="testuser", github_token="fake_github_token", linkedin_token="fake_token", linkedin_id="123456789")
    with client.application.app_context():
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

    response = client.post("/webhook/github", data=body, headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"status": "success", "linkedin_post_id": "linkedin_post_123"}


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
