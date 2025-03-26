# backend/services/verify_signature.py
import os
import hmac
import hashlib

def verify_github_signature(request, signature):
    if not signature:
        return False

    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode("utf-8")
    payload = request.data

    computed_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)
