# backend/services/verify_signature.py
import os
import hmac
import hashlib
import logging

def verify_github_signature(request, signature):
    if not signature:
        logging.warning("[Signature Verification] Missing signature in request.")
        return False

    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode("utf-8")
    payload = request.data

    computed_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_signature, signature):
        logging.warning("[Signature Verification] Signature mismatch.")
        return False

    return True
