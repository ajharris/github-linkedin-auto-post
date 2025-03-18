import pytest
from backend.app import create_app

@pytest.fixture
def client():
    """Creates a test client for the Flask app, ensuring the app context is loaded."""
    print("=== Creating Flask App in conftest.py ===")
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        print("=== Routes in conftest.py ===")
        for rule in app.url_map.iter_rules():
            print(rule)
        print("=============================")
        with app.test_client() as client:
            yield client
