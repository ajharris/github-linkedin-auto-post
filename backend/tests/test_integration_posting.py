import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_linkedin_post(client):
    """Test POST request to /auth/linkedin"""
    response = client.post("/auth/linkedin", json={"linkedin_token": "test_token", "linkedin_id": "test_id"})
    assert response.status_code == 200
    assert response.get_json() == {"message": "LinkedIn account linked successfully."}