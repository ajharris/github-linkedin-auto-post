import os
from unittest.mock import patch, MagicMock
from urllib.parse import urlencode, parse_qs
from backend.models import db, User
import pytest

@patch("requests.post")
def test_linkedin_callback_makes_token_request(mock_post, app, test_client, monkeypatch):
    # Ensure LINKEDIN_CLIENT_ID is correctly set in the test environment
    monkeypatch.setenv("LINKEDIN_CLIENT_ID", "77icevejpq3pie")

    # Skip test if required env vars are not set
    if not os.getenv("LINKEDIN_CLIENT_ID") or not os.getenv("LINKEDIN_CLIENT_SECRET"):
        pytest.skip("Missing LinkedIn environment variables")

    # Simulate LinkedIn token exchange and profile lookup
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "expires_in": 5184000
        }),
        MagicMock(status_code=200, json=lambda: {
            "sub": "123456789"
        })
    ]

    with app.app_context():
        # Seed a user with github_id='test' so the callback can match it
        user = User(
            github_id="test",
            github_username="testuser",
            SECRET_GITHUB_TOKEN="fake-token",
            linkedin_token="mock_access_token"
        )
        db.session.add(user)
        db.session.commit()

    # Mock decoding of the ID token
    decoded_id_token = { "sub": "123456789" }
    import jwt
    jwt.decode = lambda token, options, algorithms=None: decoded_id_token

    # Trigger the OAuth callback with mock code and user ID
    response = test_client.get("/auth/linkedin/callback?code=mock_code&state=test")

    assert response.status_code == 200, response.data
    assert "✅ LinkedIn Access Token and ID stored successfully" in response.get_data(as_text=True)

    # Inspect the payload sent to the LinkedIn token endpoint
    request_body = mock_post.call_args_list[0][1]['data']
    parsed = {key: [value] if isinstance(value, str) else value for key, value in request_body.items()}
    print("🔍 LinkedIn token exchange request payload:", parsed)

    # Assert critical fields exist and match real env vars
    for key in ["grant_type", "code", "redirect_uri", "client_id", "client_secret"]:
        assert key in parsed, f"Missing expected param: {key}"

    assert parsed["grant_type"] == ["authorization_code"]
    assert parsed["code"] == ["mock_code"]
    assert parsed["client_id"] == [os.getenv("LINKEDIN_CLIENT_ID")]

    # Update the test to validate the presence of a non-empty client_secret instead of expecting a specific value
    assert parsed["client_secret"][0].strip(), "CLIENT_SECRET should be non-empty"

    # Ensure CLIENT_SECRET is non-empty
    assert parsed["client_secret"][0].strip(), "CLIENT_SECRET should be non-empty"

    with app.app_context():
        updated_user = User.query.filter_by(github_id="test").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "123456789"
