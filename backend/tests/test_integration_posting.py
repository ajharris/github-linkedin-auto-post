import pytest
from backend.app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Ensure SECRET_GITHUB_user_id is set in the session for the test
def test_linkedin_post(client):
    with client.session_transaction() as sess:
        sess['SECRET_GITHUB_user_id'] = 'test_user_id'  # Mock user ID

    response = client.post(
        "/auth/linkedin",
        json={"linkedin_token": "test_token", "linkedin_id": "test_id"},
    )
    assert response.status_code == 200
