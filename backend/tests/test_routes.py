import os
import json
import pytest
from unittest.mock import patch, MagicMock
import hmac
import hashlib
import backend
from backend.routes import routes
from backend.models import db, User
from backend.app import create_app

# Set test environment variables
os.environ["LINKEDIN_ACCESS_TOKEN"] = "test_token"
os.environ["LINKEDIN_USER_ID"] = "test_user_id"
os.environ["SECRET_GITHUB_SECRET"] = "t4keth1s"


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
    with client.session_transaction() as session:
        session["SECRET_GITHUB_user_id"] = "test"  # Set a valid GitHub user ID


    response = client.get("/auth/linkedin")
    assert response.status_code == 302
    assert "https://www.linkedin.com/oauth/v2/authorization" in response.location


@patch("requests.get")
@patch("requests.post")
def test_linkedin_callback_success(mock_post, mock_get, client):
    """Test LinkedIn OAuth callback"""
    # Mock token exchange
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "test_token",
        "id_token": "mock_id_token",
    }

    # Mock profile fetch
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"sub": "123456789"}

    # Add fake GitHub user so the callback logic finds them
    with client.application.app_context():
        user = User(SECRET_GITHUB_id="test", SECRET_GITHUB_TOKEN="fake-token")
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


def testGITHUB_webhook_no_signature(client):
    """Test GitHub webhook request with missing signature."""
    response = client.post(
        "/webhook/github",
        json={"test": "data"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 403
    assert response.get_json() == {"error": "Invalid signature"}


@patch(
    "backend.routes.post_to_linkedin",
    return_value=MagicMock(status_code=201, json=lambda: {"id": "test-post-id"}),
)
@patch("backend.routes.verifyGITHUB_signature", return_value=True)
def testGITHUB_webhook(mock_verify, mock_post, client):
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

    secret = os.getenv("SECRET_GITHUB_SECRET").encode()
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    headers = {
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",  # Added missing event type header
    }

    response = client.post("/webhook/github", data=body, headers=headers)

    assert response.status_code == 200, response.data
    assert response.get_json() == {
        "status": "success",
        "linkedin_post_id": "test-post-id",
    }


@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()

        db.drop_all()


def testGITHUB_status_returns_user_info(client):
    """Test the /api/github/<SECRET_GITHUB_id>/status route."""
    # Create a mock user with GitHub details
    with client.application.app_context():
        user = User(
            SECRET_GITHUB_id="123456",
            SECRET_GITHUB_username="octocat",
            SECRET_GITHUB_TOKEN="fake-token",
        )
        db.session.add(user)
        db.session.commit()

    # Include the SECRET_GITHUB_user_id cookie in the request
    client.set_cookie("SECRET_GITHUB_user_id", "123456")
    response = client.get("/api/github/123456/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "linked": False,
        "SECRET_GITHUB_id": "123456",
        "SECRET_GITHUB_username": "octocat",
        "linkedin_id": None,
    }


@patch("requests.post")
@patch("requests.get")
def testGITHUB_login_redirect(mock_get, mock_post, client):
    """Test that the GitHub login route redirects to GitHub's OAuth URL."""
    response = client.get("/auth/github")
    assert response.status_code == 302
    assert "https://github.com/login/oauth/authorize" in response.location
    assert "client_id=" in response.location
    assert "redirect_uri=" in response.location
    assert "scope=repo" in response.location


@patch("requests.post")
@patch("requests.get")
def testGITHUB_callback_valid_code(mock_get, mock_post, client, app):
    """Test that the GitHub callback route handles a valid code."""
    # Mock token exchange response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "mocked_token"}

    # Mock user info fetch response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": "12345",
        "login": "testuser",
        "name": "Test User",
        "email": "testuser@example.com",
        "avatar_url": "https://example.com/avatar.png",
    }

    response = client.get("/auth/github/callback?code=valid_code")
    assert response.status_code == 302
    assert "SECRET_GITHUB_user_id=12345" in response.location

    # Verify user is stored in the database
    with app.app_context():
        user = User.query.filter_by(SECRET_GITHUB_id="12345").first()
        assert user is not None
        assert user.SECRET_GITHUB_username == "testuser"
        assert user.SECRET_GITHUB_TOKEN == "mocked_token"


@patch("requests.post")
def testGITHUB_callback_invalid_code(mock_post, client):
    """Test that the GitHub callback route handles an invalid code."""
    # Mock token exchange failure
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"error": "bad_verification_code"}

    response = client.get("/auth/github/callback?code=invalid_code")
    assert response.status_code == 400
    assert "Failed to obtain GitHub access token" in response.get_data(as_text=True)


@patch("requests.post")
@patch("requests.get")
def testGITHUB_callback_duplicate_user(mock_get, mock_post, client, app):
    """Test that the GitHub callback route handles duplicate users."""
    # Mock token exchange response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "mocked_token"}

    # Mock user info fetch response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": "12345",
        "login": "testuser",
        "name": "Test User",
        "email": "testuser@example.com",
        "avatar_url": "https://example.com/avatar.png",
    }

    # Add a user with the same GitHub ID to the database
    with app.app_context():
        user = User(
            SECRET_GITHUB_id="12345",
            SECRET_GITHUB_username="existinguser",
            SECRET_GITHUB_TOKEN="existing_token",
        )
        db.session.add(user)
        db.session.commit()

    response = client.get("/auth/github/callback?code=valid_code")
    assert response.status_code == 302
    assert "SECRET_GITHUB_user_id=12345" in response.location

    # Verify that the existing user was updated
    with app.app_context():
        user = User.query.filter_by(SECRET_GITHUB_id="12345").first()
        assert user is not None
        assert user.SECRET_GITHUB_username == "testuser"
        assert user.SECRET_GITHUB_TOKEN == "mocked_token"
        assert user.name == "Test User"
        assert user.email == "testuser@example.com"
        assert user.avatar_url == "https://example.com/avatar.png"


@patch("backend.services.linkedin_oauth.exchange_code_for_access_token")
def test_exchange_code_for_access_token(mock_exchange, client):
    """Test exchanging LinkedIn authorization code for access token"""
    mock_exchange.return_value = "mock_access_token"

    # Simulate calling the function
    access_token = mock_exchange("valid_code")

    assert access_token == "mock_access_token"
    mock_exchange.assert_called_once_with("valid_code")


@patch("backend.services.linkedin_oauth.link_linkedin_account")
def test_link_linkedin_account(mock_link, client):
    """Test linking LinkedIn account to GitHub user"""
    mock_link.return_value = "mock_access_token"

    # Simulate calling the function
    access_token = mock_link("testGITHUB_user_id", "valid_code")

    assert access_token == "mock_access_token"
    mock_link.assert_called_once_with("testGITHUB_user_id", "valid_code")


def test_preview_linkedin_post_single_commit(client):
    payload = {
        "commits": [
            {
                "message": "Initial commit",
                "url": "https://github.com/example/repo/commit/abc123",
                "author": {"name": "John Doe"}
            }
        ],
        "repository": {"name": "example-repo", "url": "https://github.com/example/repo"}
    }
    response = client.post("/api/preview_linkedin_post", json=payload)
    assert response.status_code == 200
    assert "Initial commit" in response.json["preview"]

def test_preview_linkedin_post_multiple_commits(client):
    payload = {
        "commits": [
            {
                "message": "Fix bug",
                "url": "https://github.com/example/repo/commit/def456",
                "author": {"name": "Jane Smith"}
            },
            {
                "message": "Add feature",
                "url": "https://github.com/example/repo/commit/ghi789",
                "author": {"name": "John Doe"}
            }
        ],
        "repository": {"name": "example-repo", "url": "https://github.com/example/repo"}
    }
    response = client.post("/api/preview_linkedin_post", json=payload)
    assert response.status_code == 200
    assert "Fix bug" in response.json["preview"]
    assert "Add feature" in response.json["preview"]

def test_preview_linkedin_post_invalid_payload(client):
    payload = {}
    response = client.post("/api/preview_linkedin_post", json=payload)
    assert response.status_code == 400
    assert "error" in response.json


@pytest.fixture
def mock_generate_digest_post():
    with patch("backend.routes.generate_digest_post") as mock:
        mock.side_effect = None  # Ensure no exception is raised
        mock.return_value = "Here's a summary of recent GitHub activity:"  # Valid response for success test
        yield mock

def test_preview_linkedin_digest_success(client, mock_generate_digest_post):
    mock_generate_digest_post.return_value = "Here's a summary of recent GitHub activity:"
    payload = {
        "events": [
            {
                "repository": {"name": "repo1"},
                "head_commit": {"message": "Fix bug", "author": {"name": "Alice"}}
            }
        ]
    }
    response = client.post("/api/preview_linkedin_digest", json=payload)
    assert response.status_code == 200
    assert "Here's a summary of recent GitHub activity:" in response.json["preview"]

def test_preview_linkedin_digest_invalid_payload(client):
    payload = {}
    response = client.post("/api/preview_linkedin_digest", json=payload)
    assert response.status_code == 400
    assert "error" in response.json

def test_preview_linkedin_digest_openai_failure(client, mocker):
    mocker.patch(
        "backend.routes.generate_digest_post",  # Correct module path
        side_effect=Exception("OpenAI API error"),
    )

    payload = {
        "events": [
            {
                "repository": {"name": "repo1"},
                "head_commit": {"message": "Fix bug", "author": {"name": "Alice"}}
            }
        ]
    }

    response = client.post("/api/preview_linkedin_digest", json=payload)

    assert response.status_code == 500
    assert response.is_json
    data = response.get_json()
    assert "error" in data