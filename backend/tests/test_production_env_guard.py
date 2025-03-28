import os
import pytest

REQUIRED_PRODUCTION_ENV_VARS = [
    "LINKEDIN_ACCESS_TOKEN",
    "LINKEDIN_USER_ID",
    "GITHUB_SECRET",
    "SQLALCHEMY_DATABASE_URI"
]

@pytest.mark.production_guard
def test_production_env_vars_set():
    """
    Fails if required production environment variables are missing.
    Intended to simulate Heroku dyno environment before deployment.
    """
    missing = [var for var in REQUIRED_PRODUCTION_ENV_VARS if not os.getenv(var)]
    assert not missing, f"❌ Missing production env vars: {missing}"

@pytest.mark.production_guard
def test_required_env_vars_for_production():
    assert os.environ.get("LINKEDIN_ACCESS_TOKEN"), "LINKEDIN_ACCESS_TOKEN is missing"
    assert os.environ.get("LINKEDIN_USER_ID"), "LINKEDIN_USER_ID is missing"

@pytest.mark.production_guard
def test_required_env_vars_for_production(monkeypatch):
    if os.getenv("SKIP_PRODUCTION_ENV_TESTS") == "1":
        pytest.skip("Skipping production env guard test in dev")

    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)

    assert os.environ.get("LINKEDIN_ACCESS_TOKEN"), "LINKEDIN_ACCESS_TOKEN is missing"
    assert os.environ.get("LINKEDIN_USER_ID"), "LINKEDIN_USER_ID is missing"
