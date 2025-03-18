import hmac
import hashlib
import os

def generate_signature(payload):
    """Generate HMAC SHA256 signature for GitHub webhook verification."""
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "test_secret").encode()
    mac = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return f"sha256={mac}"
