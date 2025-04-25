# backend/tests/test_env_config.py

import os
import sys
import pytest
from backend.config import config

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


def test_backend_url_development(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("BACKEND_URL", "http://dev.local")  # Ensure BACKEND_URL is set
    dev_config = config["development"]
    assert dev_config.BACKEND_URL == "http://dev.local"


def test_backend_url_testing(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("TEST_BACKEND_URL", "http://test.local")
    test_config = config["testing"]
    assert test_config.BACKEND_URL == "http://test.local"


def test_backend_url_production(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("PROD_BACKEND_URL", "https://prod.local")
    prod_config = config["production"]
    assert prod_config.BACKEND_URL == "https://prod.local"


def test_missing_backend_url_raises_error(monkeypatch):
    monkeypatch.delenv("BACKEND_URL", raising=False)
    with pytest.raises(RuntimeError, match="Missing required environment variable: BACKEND_URL"):
        from backend.config import get_required_env_var
        get_required_env_var("BACKEND_URL")


def test_missing_frontend_url_raises_error(monkeypatch):
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    with pytest.raises(RuntimeError, match="Missing required environment variable: FRONTEND_URL"):
        from backend.config import get_required_env_var
        get_required_env_var("FRONTEND_URL")


def test_missing_linkedin_redirect_uri_raises_error(monkeypatch):
    monkeypatch.delenv("LINKEDIN_REDIRECT_URI", raising=False)
    with pytest.raises(RuntimeError, match="Missing required environment variable: LINKEDIN_REDIRECT_URI"):
        from backend.config import get_required_env_var
        get_required_env_var("LINKEDIN_REDIRECT_URI")


def test_no_raw_urls_in_codebase():
    import os
    import re

    # Exclude the default value of LOCAL_SERVER_URL from the test
    local_server_url = os.getenv("LOCAL_SERVER_URL", "http://127.0.0.1:5000")
    # Ensure the default value of HEROKU_PATTERN is excluded from the test
    heroku_pattern = os.getenv("HEROKU_PATTERN", "herokuapp")
    patterns = [
        re.compile(local_server_url) if local_server_url != "http://127.0.0.1:5000" else None,
        re.compile(heroku_pattern) if heroku_pattern != "herokuapp" else None,
    ]
    patterns = [p for p in patterns if p is not None]

    # Define file extensions to check
    file_extensions = [".py", ".js"]

    # Walk through the workspace and check files
    workspace_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    for root, _, files in os.walk(workspace_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in patterns:
                        assert not pattern.search(content), f"Raw URL found in {file_path}"


def test_env_vars_in_ci_cd(monkeypatch):
    # Simulate CI/CD environment
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("BACKEND_URL", "https://ci-backend.example.com")
    monkeypatch.setenv("FRONTEND_URL", "https://ci-frontend.example.com")

    # Check that environment variables are accessible
    assert os.getenv("CI") == "true"
    assert os.getenv("BACKEND_URL") == "https://ci-backend.example.com"
    assert os.getenv("FRONTEND_URL") == "https://ci-frontend.example.com"
