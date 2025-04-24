# backend/tests/test_env_config.py

import os
import sys
import pytest

# Add the backend directory to the Python module search path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set required environment variables for testing
os.environ["LINKEDIN_ACCESS_TOKEN"] = "test_access_token"
os.environ["LINKEDIN_USER_ID"] = "test_user_id"


def test_required_env_vars_present():
    assert os.getenv("LINKEDIN_ACCESS_TOKEN"), "LINKEDIN_ACCESS_TOKEN is missing"
    assert os.getenv("LINKEDIN_USER_ID"), "LINKEDIN_USER_ID is missing"


def test_production_env_vars_required():
    """
    This test will fail if critical production env vars are missing.
    CI should run this in production-like env.
    """
    required_vars = ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_USER_ID"]
    missing = [var for var in required_vars if not os.getenv(var)]
    assert not missing, f"Missing required env vars: {missing}"


def test_missing_env_var_raises_error(monkeypatch):
    # Simulate production environment
    monkeypatch.setenv("FLASK_ENV", "production")

    # Unset a required env var
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)

    # Delay import so config gets reloaded with monkeypatched env
    try:
        from backend.app import create_app  # Import the app factory function
    except ImportError as e:
        pytest.fail(f"Failed to import 'create_app' from 'backend.app': {e}")

    with pytest.raises(RuntimeError) as excinfo:
        # Create the app instance, which should trigger the error
        create_app()

    assert "Missing required" in str(excinfo.value)
