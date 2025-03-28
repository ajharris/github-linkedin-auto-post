import pytest
from backend.services.post_to_linkedin import post_to_linkedin
import os

@pytest.mark.production_guard
def test_required_env_vars_for_production(monkeypatch):
    """Ensure app fails loudly if required LinkedIn env vars are missing in prod."""
    
    if os.getenv("SKIP_PRODUCTION_ENV_TESTS") == "1":
        pytest.skip("Skipping production env guard test in local/dev")

    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("LINKEDIN_USER_ID", raising=False)
    

    with pytest.raises(ValueError, match="Missing LinkedIn credentials"):
        post_to_linkedin("some-repo", "Test commit message")
