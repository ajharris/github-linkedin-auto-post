import pytest
import requests
from flask import url_for
from urllib.parse import urlparse, parse_qs
from backend.app import create_app
from backend.models import db, User


@pytest.fixture(scope="module")
def test_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield app.test_client()

    db.drop_all()
    ctx.pop()


def test_linkedin_auth_redirect(test_client):
    user = User(
        SECRET_GITHUB_id="123",
        SECRET_GITHUB_TOKEN="test-token",
        SECRET_GITHUB_username="octocat",
        linkedin_token="old-token",
        linkedin_id="old-id",
    )
    db.session.add(user)
    db.session.commit()

    response = test_client.get("/auth/linkedin?SECRET_GITHUB_user_id=123")
    assert response.status_code == 302  # redirect
    assert "linkedin.com/oauth/v2/authorization" in response.location

    # Make sure LinkedIn info is cleared
    updated = User.query.filter_by(SECRET_GITHUB_id="123").first()
    assert updated.linkedin_token is None
    assert updated.linkedin_id is None


def test_linkedin_callback_success(test_client, requests_mock):
    # Simulate LinkedIn token and id_token response
    requests_mock.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        json={"access_token": "test-access-token", "id_token": "fake.id.token"},
    )

    # Simulate decoded ID token (JWT decoding is disabled in app logic anyway)
    decoded_id_token = {"sub": "linkedin-user-12345"}

    # Patch jwt.decode to return our fake decoded ID token
    import jwt

    original_decode = jwt.decode
    jwt.decode = lambda *_args, **_kwargs: decoded_id_token

    # Set up user in database
    user = User(
        SECRET_GITHUB_id="123", SECRET_GITHUB_TOKEN="test-token", SECRET_GITHUB_username="octocat"
    )
    db.session.add(user)
    db.session.commit()

    response = test_client.get("/auth/linkedin/callback?code=fake-code&state=123")
    assert response.status_code == 200
    assert "LinkedIn Access Token and ID stored" in response.get_data(as_text=True)

    updated = User.query.filter_by(SECRET_GITHUB_id="123").first()
    assert updated.linkedin_token == "test-access-token"
    assert updated.linkedin_id == "linkedin-user-12345"

    # Restore original JWT decode
    jwt.decode = original_decode


def test_linkedin_callback_missing_code(test_client):
    response = test_client.get("/auth/linkedin/callback")
    assert response.status_code == 400
    assert "Authorization failed" in response.get_data(as_text=True)
