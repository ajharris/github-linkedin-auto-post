import pytest
from backend.app import create_app
from backend.models import db, User

@pytest.fixture(scope="module")
def test_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()

        db.drop_all()


def test_github_status_returns_user_info(test_client):
    """Test the /api/github/<github_id>/status route."""
    # Create a mock user with GitHub details
    with test_client.application.app_context():
        user = User(
            github_id="123456",
            github_username="octocat",
            github_token="fake-token"
        )
        db.session.add(user)
        db.session.commit()

    # Include the github_user_id cookie in the request
    test_client.set_cookie("github_user_id", "123456")
    response = test_client.get("/api/github/123456/status")
    
    assert response.status_code == 200
    assert response.get_json() == {
        "linked": False,
        "github_id": "123456",
        "github_username": "octocat",
        "linkedin_id": None
    }
