import os
import json
import pytest
from unittest.mock import patch
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
    mock_post.return_value.json.return_value = {"access_token": "test_token"}

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

    assert response.status_code == 200
    assert b"LinkedIn Access Token stored successfully" in response.data



def test_linkedin_callback_no_code(client):
    """Test LinkedIn OAuth callback failure due to missing code"""
    response = client.get("/auth/linkedin/callback")
    assert response.status_code == 400
    assert "Authorization failed" in response.get_data(as_text=True)


def test_github_webhook_no_signature(client):
    """Test GitHub webhook request with missing signature"""
    response = client.post("/webhook/github", json={"test": "data"}, headers={"Content-Type": "application/json"})
    assert response.status_code == 403
    assert response.get_json() == {"error": "Invalid signature"}


@patch("backend.routes.post_to_linkedin", return_value={"id": "test-post-id"})
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
        "repository": {"full_name": "ajharris/github-linkedin-auto-post"},
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

    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}
