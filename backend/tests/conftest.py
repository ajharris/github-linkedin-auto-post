import pytest
from backend.app import app as flask_app  # ✅ Import app but rename it to avoid conflicts
from backend.models import db
from unittest.mock import patch

@pytest.fixture(scope="session")
def app():
    """Provide the actual Flask app for testing."""
    return flask_app  # ✅ Use the imported app without overriding its name

@pytest.fixture(scope="session")
def client(app):
    """Use the real Flask app's test client."""
    return app.test_client()
