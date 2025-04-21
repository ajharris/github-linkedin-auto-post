import pytest
import requests_mock
from urllib.parse import parse_qs, urlencode
from backend.models import User, db
from unittest.mock import patch, MagicMock

@patch("requests.post")
def test_linkedin_callback_makes_token_request(mock_post, app, test_client):
    mock_post.return_value.status_code = 200

    # Ensure the mock response for the token exchange is not overwritten
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

    # Mock LinkedIn profile response with numeric member ID
    mock_post.return_value.json.return_value = {
        "sub": "123456789"
    }

    # Mock decoding of the ID token
    decoded_id_token = {
        "sub": "123456789"
    }
    import jwt
    jwt.decode = lambda token, options, algorithms=None: decoded_id_token  # Fix mock to handle 'algorithms' argument

    # Trigger the OAuth callback with mock code and user ID
    response = test_client.get("/auth/linkedin/callback?code=mock_code&state=test")

    assert response.status_code == 200, response.data
    assert "✅ LinkedIn Access Token and ID stored successfully" in response.get_data(as_text=True)

    # Inspect payload to LinkedIn token endpoint
    # Ensure the `request_body` is URL-encoded before parsing
    request_body = urlencode(mock_post.call_args[1]['data'])
    parsed = parse_qs(request_body)
    print("🔍 LinkedIn token exchange request payload:", parsed)

    for key in ["grant_type", "code", "redirect_uri", "client_id", "client_secret"]:
        assert key in parsed, f"Missing expected param: {key}"

    assert parsed["grant_type"] == ["authorization_code"]
    assert parsed["code"] == ["mock_code"]

    with app.app_context():
        updated_user = User.query.filter_by(github_id="test").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "123456789"


