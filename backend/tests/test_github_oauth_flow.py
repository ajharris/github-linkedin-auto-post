import pytest
from backend.app import create_app
from backend.models import db, User


@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()

        db.drop_all()


def testGITHUB_status_returns_user_info(client):
    """Test the /api/github/<SECRET_GITHUB_id>/status route."""
    # Create a mock user with GitHub details
    with client.application.app_context():
        user = User(
            SECRET_GITHUB_id="123456",
            SECRET_GITHUB_username="octocat",
            SECRET_GITHUB_TOKEN="fake-token",
        )
        db.session.add(user)
        db.session.commit()

    # Include the SECRET_GITHUB_user_id cookie in the request
    client.set_cookie("SECRET_GITHUB_user_id", "123456")
    response = client.get("/api/github/123456/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "linked": False,
        "SECRET_GITHUB_id": "123456",
        "SECRET_GITHUB_username": "octocat",
        "linkedin_id": None,
    }
