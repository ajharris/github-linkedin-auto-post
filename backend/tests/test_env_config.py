# backend/tests/test_env_config.py

import os

def test_required_env_vars_present():
    assert os.getenv("LINKEDIN_ACCESS_TOKEN"), "LINKEDIN_ACCESS_TOKEN is missing"
    assert os.getenv("LINKEDIN_USER_ID"), "LINKEDIN_USER_ID is missing"
    
