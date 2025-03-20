import os
import json
import pytest
from unittest.mock import patch
from flask import Flask
from backend.routes import routes, verify_github_signature
from backend.models import db, User, GitHubEvent
import hmac, hashlib

@pytest.fixture
def app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(routes)
    return app

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
    assert response.status_code == 302  # Should redirect
    assert "https://www.linkedin.com/oauth/v2/authorization" in response.location

@patch("requests.post")
def test_linkedin_callback_success(mock_post, client):
    """Test LinkedIn OAuth callback"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "test_token"}

    response = client.get("/auth/linkedin/callback?code=valid_code")
    assert response.status_code == 200
    assert "Your LinkedIn Access Token" in response.text

def test_linkedin_callback_no_code(client):
    """Test LinkedIn OAuth callback failure due to missing code"""
    response = client.get("/auth/linkedin/callback")
    assert response.status_code == 400
    assert "Authorization failed" in response.text

def test_github_webhook_no_signature(client):
    """Test GitHub webhook request with missing signature"""
    response = client.post("/webhook/github", data=json.dumps({"test": "data"}), headers={"Content-Type": "application/json"})
    assert response.status_code == 403
    assert response.json == {"error": "Invalid signature"}

@patch("routes.verify_github_signature", return_value=True)
@patch("models.User.query.filter_by")
def test_github_webhook_push_event(mock_filter_by, mock_verify, client):
    """Test handling a GitHub push event"""
    mock_filter_by.return_value.first.return_value = User(id=1, github_id="testuser", github_token="token")

    payload = {
        "repository": {"full_name": "test/repo"},
        "head_commit": {"message": "Test commit", "url": "http://github.com/test"},
        "pusher": {"name": "testuser"}
    }

    response = client.post("/webhook/github", data=json.dumps(payload), headers={
        "X-GitHub-Event": "push",
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=test_signature"
    })

    assert response.status_code == 200
    assert "GitHub push event stored successfully" in response.json["message"]

def test_verify_github_signature():
    """Test verifying a valid GitHub webhook signature"""
    secret = b"test_secret"
    payload = b'{"test": "data"}'
    signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()

    with patch.dict(os.environ, {"GITHUB_SECRET": "test_secret"}):
        assert verify_github_signature(payload, signature) is True

    assert verify_github_signature(payload, "invalid_signature") is False
