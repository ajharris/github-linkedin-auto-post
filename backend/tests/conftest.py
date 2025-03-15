import sys
import os

# Ensure backend/ is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from backend.app import create_app

@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
