import pytest
from backend.app import create_app
from backend.models import db, User

@pytest.fixture(scope="module")
def test_client():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ✅ Only manage context here, not nested later
    ctx = app.app_context()
    ctx.push()

    db.create_all()

    yield app.test_client()

    db.drop_all()
    ctx.pop()


def test_github_status_returns_user_info(test_client):
    # Create a mock user with GitHub details
    user = User(
        github_id="123456",
        github_username="octocat",
        github_token="fake-token"
    )
    db.session.add(user)
    db.session.commit()

    response = test_client.get("/api/github/123456/status")
    assert response.status_code == 200

    data = response.get_json()
    assert data["github_id"] == "123456"
    assert data["github_username"] == "octocat"
    assert data["linked"] is False
