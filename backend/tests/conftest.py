import os
import pytest
from unittest.mock import patch
from backend.app import create_app, db

REQUIRED_ENV_VARS = ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_USER_ID"]

@pytest.fixture(scope="session", autouse=True)
def check_env_vars():
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        pytest.fail(f"Missing required environment variables: {', '.join(missing_vars)}")

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(config_name="testing")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def test_client(app):
    """Flask test client that shares the app context."""
    return app.test_client()

@pytest.fixture
def patch_signature_verification():
    """Automatically bypass GitHub signature checks."""
    with patch("backend.routes.verify_github_signature", return_value=True):
        yield

# Removed the patch_env fixture to ensure tests fail if required environment variables are not set.

# Optional: a named variant if you want to override patch_env in specific tests
@pytest.fixture
def patch_linkedin_env(monkeypatch):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "test_token")
    monkeypatch.setenv("LINKEDIN_USER_ID", "urn:li:member:testuser")

@pytest.fixture(autouse=True)
def clean_db(app):
    from backend.models import db
    db.session.remove()
    db.drop_all()
    db.create_all()

@pytest.fixture(autouse=True)
def patch_post_to_linkedin():
    with patch("backend.routes.post_to_linkedin") as mock_func:
        mock_func.side_effect = lambda user, repo, msg: type("Response", (), {
            "status_code": 201,
            "json": "{'id': 'mocked-id'}"  # Replaced lambda with string
        })()
        yield mock_func

