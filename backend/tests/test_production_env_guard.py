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
