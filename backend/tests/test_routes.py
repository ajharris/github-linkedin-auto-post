import os
import json
import pytest
from unittest.mock import patch
from flask import Flask
from backend.routes import routes, verify_github_signature
from backend.models import db, User, GitHubEvent
import hmac, hashlib
from backend.app import app




@pytest.fixture
def client(app):
    with app.app_context():
        with app.test_client() as client:  # ✅ Ensures the client is properly created inside app context
            yield client




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
    response = client.post("/webhook/github", json={"test": "data"}, headers={"Content-Type": "application/json"})
    
    # ✅ Check response text if available
    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json)

    assert response.status_code == 403, f"Expected 403 but got {response.status_code}"
    assert response.json == {"error": "Invalid signature"}

@patch("backend.routes.verify_github_signature", return_value=True)
def test_github_webhook_push_event(mock_verify, client):
    """Test handling a GitHub push event"""

    print("Flask App Name:", client.application.name)
    print("Available routes in test:", [rule.rule for rule in client.application.url_map.iter_rules()])

    with client.application.app_context():
        existing_user = User.query.filter_by(github_id="testuser").first()
        if not existing_user:  # ✅ Only add if the user does not already exist
            test_user = User(id=1, github_id="testuser", github_token="token")
            db.session.add(test_user)
            db.session.commit()  # ✅ Ensure user is saved

    # Debugging: Check if user was created
    with client.application.app_context():
        db_user = User.query.filter_by(github_id="testuser").first()
        print("User in DB:", db_user)

    payload = {
        "repository": {"full_name": "test/repo"},
        "head_commit": {"message": "Test commit", "url": "http://github.com/test"},
        "pusher": {"name": "testuser"}
    }

    response = client.post("/webhook/github", json=payload, headers={
        "X-GitHub-Event": "push",
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=test_signature"
    })

    print("Response Status Code:", response.status_code)
    print("Response JSON:", response.json)

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert "GitHub push event stored successfully" in response.json["message"]
