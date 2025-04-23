import os
from unittest.mock import patch, MagicMock
from urllib.parse import urlencode, parse_qs
from backend.models import db, User
import pytest


def get_linkedin_client_id():
    return os.environ.get("LINKEDIN_CLIENT_ID", "mock_client_id")  # Added fallback


def get_linkedin_client_secret():
    return os.environ.get(
        "LINKEDIN_CLIENT_SECRET", "mock_client_secret"
    )  # Added fallback


@patch("requests.post")
def test_linkedin_callback_makes_token_request(
    mock_post, app, test_client, monkeypatch
):
    # Set environment variables explicitly for the test
    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "mock_client_id")
    monkeypatch.setenv("LINKEDIN_CLIENT_SECRET", "mock_client_secret")

    # Set application config explicitly for the test
    app.config["LINKEDIN_CLIENT_ID"] = "mock_client_id"
    app.config["LINKEDIN_CLIENT_SECRET"] = "mock_client_secret"

    # Fail early if env vars are not provided (moved after monkeypatch)
    linkedin_client_id = get_linkedin_client_id()
    linkedin_client_secret = get_linkedin_client_secret()
    assert linkedin_client_id, "Missing LINKEDIN_CLIENT_ID in environment"
    assert linkedin_client_secret, "Missing LINKEDIN_CLIENT_SECRET in environment"

    # Simulate LinkedIn token exchange and profile lookup
    mock_post.side_effect = [
        MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "mock_access_token",
                "id_token": "mock_id_token",
                "expires_in": 5184000,
            },
        ),
        MagicMock(status_code=200, json=lambda: {"sub": "123456789"}),
    ]

    with app.app_context():
        # Seed a user with github_id='test'
        user = User(
            github_id="test",
            github_username="testuser",
            SECRET_GITHUB_TOKEN="fake-token",
            linkedin_token="mock_access_token",
        )
        db.session.add(user)
        db.session.commit()

    # Mock decoding of the ID token
    import jwt

    jwt.decode = lambda token, options, algorithms=None: {"sub": "123456789"}

    # Trigger the OAuth callback
    response = test_client.get("/auth/linkedin/callback?code=mock_code&state=test")

    assert response.status_code == 200, response.data
    assert "✅ LinkedIn Access Token and ID stored successfully" in response.get_data(
        as_text=True
    )

    # Inspect the request payload
    request_body = mock_post.call_args_list[0][1]["data"]
    parsed = {
        key: [value] if isinstance(value, str) else value
        for key, value in request_body.items()
    }
    print("🔍 LinkedIn token exchange request payload:", parsed)

    # Check all expected fields are present
    for key in ["grant_type", "code", "redirect_uri", "client_id", "client_secret"]:
        assert key in parsed, f"Missing expected param: {key}"

    # Validate values are present and well-formed
    assert parsed["client_id"][0].strip(), "CLIENT_ID should be non-empty"
    assert parsed["client_secret"][0].strip(), "CLIENT_SECRET should be non-empty"
    assert parsed["grant_type"] == ["authorization_code"]
    assert parsed["code"] == ["mock_code"]

    # Validate user update
    with app.app_context():
        updated_user = User.query.filter_by(github_id="test").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "123456789"
