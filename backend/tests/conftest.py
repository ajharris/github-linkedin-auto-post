import pytest
from backend.app import create_app, db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")  # Use 'testing' config
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        

@pytest.fixture
def client(app):
    """Provide a test client for the app."""
    return app.test_client()
