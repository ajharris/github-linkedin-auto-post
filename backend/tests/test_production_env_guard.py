import os
import pytest

@pytest.mark.production_guard
def test_required_env_vars_for_production(monkeypatch):
    """This test ensures the app will fail in production if env vars are missing."""

    if os.getenv("SKIP_PRODUCTION_ENV_TESTS") == "1":
        pytest.skip("Skipping production env guard test in local/dev")

    # Simulate a clean production environment
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)

    # These asserts mimic your app's startup-time requirements
    assert os.environ.get("LINKEDIN_ACCESS_TOKEN"), "LINKEDIN_ACCESS_TOKEN is missing"
    assert os.environ.get("LINKEDIN_USER_ID"), "LINKEDIN_USER_ID is missing"
