import pytest
from backend.app import create_app, db

@pytest.fixture(scope="session")
def test_app():
    """Create a Flask test app instance with an in-memory database."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()  # ✅ Ensure tables exist before tests run
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(test_app):
    """Set up a test client using the initialized test app."""
    return test_app.test_client()
