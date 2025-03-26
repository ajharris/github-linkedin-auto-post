# conftest.py
import pytest
from unittest.mock import patch
from backend.app import create_app, db

@pytest.fixture
def patch_signature_verification():
    with patch("backend.routes.verify_github_signature", return_value=True):
        yield

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "test_token")
    monkeypatch.setenv("LINKEDIN_USER_ID", "test_user_id")

@pytest.fixture(scope="function")
def app():
    app = create_app(config_name="testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(app):
    return app.test_client()
