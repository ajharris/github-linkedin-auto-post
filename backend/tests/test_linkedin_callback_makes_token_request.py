import pytest
import requests_mock
from urllib.parse import parse_qs
from backend.scripts.seed_user import seed_main_user  # optional for setup

def test_linkedin_callback_makes_token_request(app, test_client):
    with requests_mock.Mocker() as m:
        m.post("https://www.linkedin.com/oauth/v2/accessToken", json={
            "access_token": "mock_access_token",
            "expires_in": 5184000
        })

        response = test_client.get("/auth/linkedin/callback?code=mock_code")

        # ✅ Ensure request was made
        assert response.status_code in [200, 302]
        assert m.called, "Expected POST to LinkedIn was not made"

        # 🪵 Log and inspect the actual payload sent to LinkedIn
        request_body = m.last_request.text
        parsed = parse_qs(request_body)
        print("🔍 LinkedIn token exchange request payload:", parsed)

        # ✅ Assert expected keys exist in the form-encoded body
        for key in ["grant_type", "code", "redirect_uri", "client_id", "client_secret"]:
            assert key in parsed, f"Missing expected param: {key}"

        assert parsed["grant_type"] == ["authorization_code"]
        assert parsed["code"] == ["mock_code"]
