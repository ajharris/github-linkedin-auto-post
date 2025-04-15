import pytest
import requests_mock
from urllib.parse import parse_qs
from backend.models import User, db

def test_linkedin_callback_handles_id_token(app, test_client):
    with app.app_context():
        # Seed a user with github_id='123456789' so the callback can match it
        user = User(
            github_id="123456789",
            github_username="testuser",
            github_token="fake-token",
            linkedin_token=None,
            linkedin_id=None
        )
        db.session.add(user)
        db.session.commit()

    with requests_mock.Mocker() as m:
        # Mock LinkedIn access token exchange
        m.post("https://www.linkedin.com/oauth/v2/accessToken", json={
            "access_token": "mock_access_token",
            "id_token": "mock_id_token",
            "expires_in": 5184000
        })

        # Mock decoding of the ID token
        decoded_id_token = {
            "sub": "mock_linkedin_user_id",
            "email": "testuser@example.com"
        }
        import jwt
        jwt.decode = lambda token, options, algorithms: decoded_id_token

        # Trigger the OAuth callback
        response = test_client.get("/auth/linkedin/callback?code=mock_code&state=123456789")

        assert response.status_code == 200, response.data
        assert "✅ LinkedIn Access Token and ID stored successfully" in response.get_data(as_text=True)
        assert m.called, "Expected POST to LinkedIn was not made"

        # Inspect payload to LinkedIn token endpoint
        request_body = m.request_history[0].text
        parsed = parse_qs(request_body)
        print("🔍 LinkedIn token exchange request payload:", parsed)

        for key in ["grant_type", "code", "redirect_uri", "client_id", "client_secret"]:
            assert key in parsed, f"Missing expected param: {key}"

        assert parsed["grant_type"] == ["authorization_code"]
        assert parsed["code"] == ["mock_code"]

    with app.app_context():
        updated_user = User.query.filter_by(github_id="123456789").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "mock_linkedin_user_id"
