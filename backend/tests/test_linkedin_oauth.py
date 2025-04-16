from unittest.mock import patch
import pytest
from backend.models import db, User

# Fixtures
@pytest.fixture
def db_session():
    yield db.session
    db.session.rollback()

@pytest.fixture
def github_user(db_session):
    user = User(
        github_id="12345",
        github_username="testuser",
        github_token="mock_github_token"  # Added a valid value for github_token
    )
    db.session.add(user)
    db.session.commit()
    return user

# Tests

def test_linkedin_auth_redirect(client):
    response = client.get("/auth/linkedin")
    assert response.status_code == 302
    assert "https://www.linkedin.com/oauth/v2/authorization" in response.location
    assert "client_id=" in response.location
    assert "redirect_uri=" in response.location
    assert "scope=" in response.location

@patch("backend.services.linkedin_oauth.requests.post")
@patch("backend.services.linkedin_oauth.requests.get")
def test_linkedin_callback_stores_token_and_urn(mock_get, mock_post, client, db_session, github_user):
    # Token exchange mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "mock_access_token",
        "expires_in": 5184000
    }

    # Profile API mock
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": "abcd1234"
    }

    with client.session_transaction() as session:
        session["github_user_id"] = github_user.github_id  # Use valid GitHub user ID

    response = client.get(f"/auth/linkedin/callback?code=fake_code&state={github_user.github_id}")
    assert response.status_code == 302

    updated_user = db.session.get(User, github_user.id)
    assert updated_user.linkedin_token == "mock_access_token"
    assert updated_user.linkedin_id == "abcd1234"

def test_user_model_has_linkedin_fields(github_user):
    assert hasattr(github_user, "linkedin_token")  # Updated to match the model
    assert hasattr(github_user, "linkedin_id")  # Updated to match the model

def test_linkedin_status_endpoint(client, github_user, db_session):
    github_user.linkedin_token = "token123"
    github_user.linkedin_id = "urn:li:person:abcd"
    db_session.commit()

    with client.session_transaction() as session:
        session["github_user_id"] = github_user.github_id  # Set correct GitHub user ID in cookies

    res = client.get("/api/get_user_profile")
    data = res.get_json()

    assert res.status_code == 200
    assert data["linkedin_linked"] is True

@patch("backend.services.linkedin_oauth.requests.post")
def test_linkedin_callback_token_exchange_fails(mock_post, client):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"error": "invalid_request"}

    response = client.get("/auth/linkedin/callback?code=bad_code&state=xyz")
    assert response.status_code == 400
    assert b"Failed to get access token" in response.data  # Updated assertion to match actual response
