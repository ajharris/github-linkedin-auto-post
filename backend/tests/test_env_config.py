# backend/tests/test_env_config.py

import os

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


