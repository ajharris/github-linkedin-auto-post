import pytest
import requests_mock
from urllib.parse import parse_qs
from backend.models import User, db
from unittest.mock import patch


@patch("requests.post")
def test_linkedin_callback_handles_id_token(mock_post, app, test_client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "expires_in": 5184000,
    }

    with app.app_context():
        # Seed a user with SECRET_GITHUB_id='123456789' so the callback can match it
        user = User(
            SECRET_GITHUB_id="123456789",
            SECRET_GITHUB_username="testuser",
            SECRET_GITHUB_TOKEN="fake-token",
            linkedin_token=None,
            linkedin_id=None,
        )
        db.session.add(user)
        db.session.commit()

    # Mock decoding of the ID token
    decoded_id_token = {"sub": "mock_linkedin_user_id", "email": "testuser@example.com"}
    import jwt

    jwt.decode = (
        lambda token, options, algorithms=None: decoded_id_token
    )  # Fix mock to handle 'algorithms' argument

    # Trigger the OAuth callback
    response = test_client.get("/auth/linkedin/callback?code=mock_code&state=123456789")

    assert (
        response.status_code == 200
    ), response.data  # Updated to expect 200 status code in test mode
    assert "✅ LinkedIn Access Token and ID stored successfully" in response.get_data(
        as_text=True
    )

    with app.app_context():
        updated_user = User.query.filter_by(SECRET_GITHUB_id="123456789").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "mock_linkedin_user_id"
