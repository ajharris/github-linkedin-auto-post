import pytest
import requests_mock
from urllib.parse import parse_qs
from backend.models import User, db

def test_linkedin_callback_makes_token_request(app, test_client):
    with app.app_context():
        # Seed a user with github_id='test' so the callback can match it
        user = User(github_id="test", github_token="fake-token")
        db.session.add(user)
        db.session.commit()

    with requests_mock.Mocker() as m:
        # Mock LinkedIn access token exchange
        m.post("https://www.linkedin.com/oauth/v2/accessToken", json={
            "access_token": "mock_access_token",
            "expires_in": 5184000
        })

        # Mock LinkedIn profile response with numeric member ID
        m.get("https://api.linkedin.com/v2/userinfo", json={
            "sub": "123456789"
        })

        # Trigger the OAuth callback with mock code and user ID
        response = test_client.get("/auth/linkedin/callback?code=mock_code&state=test")

        assert response.status_code == 200
        assert b"LinkedIn Access Token stored successfully" in response.data
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
        updated_user = User.query.filter_by(github_id="test").first()
        assert updated_user.linkedin_token == "mock_access_token"
        assert updated_user.linkedin_id == "123456789"


