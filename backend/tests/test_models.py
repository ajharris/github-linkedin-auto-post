import pytest
from datetime import datetime, timezone

import sqlalchemy
from backend.models import db, User, GitHubEvent


@pytest.fixture
def app():
    """Create a test Flask app"""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def session(app):
    """Create a test database session"""
    with app.app_context():
        yield db.session


def test_create_user(session):
    """Test creating a user"""
    user = User(
        SECRET_GITHUB_id="123456",
        linkedin_id="654321",
        SECRET_GITHUB_TOKEN="gh_token",
        linkedin_token="li_token",
    )
    session.add(user)
    session.commit()

    fetched_user = User.query.filter_by(SECRET_GITHUB_id="123456").first()
    assert fetched_user is not None
    assert fetched_user.linkedin_id == "654321"


def test_createGITHUB_event(session):
    """Test creating a GitHub event"""
    user = User(SECRET_GITHUB_id="123456", SECRET_GITHUB_TOKEN="gh_token")
    session.add(user)
    session.commit()

    event = GitHubEvent(
        user_id=user.id,
        repo_name="test/repo",
        commit_message="Initial commit",
        commit_url="http://github.com/test",
        status="pending",
        timestamp=datetime.now(timezone.utc),
    )
    session.add(event)
    session.commit()

    fetched_event = GitHubEvent.query.filter_by(user_id=user.id).first()
    assert fetched_event is not None
    assert fetched_event.repo_name == "test/repo"
    assert fetched_event.commit_message == "Initial commit"


def testGITHUB_event_creation_with_missing_fields(session):
    """Test that GitHubEvent creation fails gracefully if required fields are missing."""
    user = User(SECRET_GITHUB_id="123456", SECRET_GITHUB_TOKEN="gh_token")
    session.add(user)
    session.commit()

    # Attempt to create an event with missing fields
    event = GitHubEvent(
        user_id=user.id,
        repo_name=None,  # Missing repo_name
        commit_message=None,  # Missing commit_message
        commit_url="http://github.com/test",
        status="pending",
        timestamp=datetime.now(timezone.utc),
    )

    with pytest.raises(
        sqlalchemy.exc.IntegrityError,
        match="NOT NULL constraint failed: git_hub_event.repo_name",
    ):
        session.add(event)
        session.commit()
