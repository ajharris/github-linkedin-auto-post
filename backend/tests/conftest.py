import os
import pytest
from unittest.mock import patch
from backend.app import create_app, db
from backend.config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET

REQUIRED_ENV_VARS = [
    "SQLALCHEMY_DATABASE_URI",
    "LINKEDIN_CLIENT_ID",
    "LINKEDIN_CLIENT_SECRET",
    "DATABASE_URL",
    "SECRET_GITHUB_TOKEN",
    "SECRET_GITHUB_SECRET",
    "SEED_GITHUB_ID",
    "SEED_GITHUB_USERNAME",
    "SEED_GITHUB_TOKEN",
    "SEED_LINKEDIN_ID",
    "SEED_LINKEDIN_TOKEN",
    "LINKEDIN_ACCESS_TOKEN",
    "LINKEDIN_USER_ID",
]

# Add default values for optional variables
DEFAULT_ENV_VALUES = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
    "LINKEDIN_CLIENT_ID": "test_client_id",
    "LINKEDIN_CLIENT_SECRET": "test_client_secret",
    "DATABASE_URL": "sqlite:///test.db",
    "SECRET_GITHUB_TOKEN": "testGITHUB_token",
    "SECRET_GITHUB_SECRET": "test_secret",
    "SEED_GITHUB_ID": "testGITHUB_id",
    "SEED_GITHUB_USERNAME": "testGITHUB_username",
    "SEED_GITHUB_TOKEN": "testGITHUB_token",
    "SEED_LINKEDIN_ID": "test_linkedin_id",
    "SEED_LINKEDIN_TOKEN": "test_linkedin_token",
    "LINKEDIN_ACCESS_TOKEN": "test_access_token",
    "LINKEDIN_USER_ID": "test_user_id",
}

for var, default in DEFAULT_ENV_VALUES.items():
    os.environ.setdefault(var, default)


@pytest.fixture(scope="session", autouse=True)
def verify_env_vars():
    """Ensure all required environment variables are set."""
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        pytest.fail(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


@pytest.fixture
def app():
    from backend.app import create_app

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.logger.info(f"[Test Config] PROPAGATE_EXCEPTIONS is set to: {app.config['PROPAGATE_EXCEPTIONS']}")

    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def test_client(app):
    """Flask test client that shares the app context."""
    return app.test_client()


@pytest.fixture
def patch_signature_verification():
    """Automatically bypass GitHub signature checks."""
    with patch("backend.routes.verifyGITHUB_signature", return_value=True):
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
        mock_func.side_effect = lambda user, repo, msg: type(
            "Response",
            (),
            {
                "status_code": 201,
                "json": "{'id': 'mocked-id'}",  # Replaced lambda with string
            },
        )()
        yield mock_func
